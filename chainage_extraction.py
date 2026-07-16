import os, sys, csv, json, sqlite3

CFG = 'chainage_config.json'
OUT = 'output_chainage'


def find_gpkg_folders(root):
    result = {}
    for dirpath, dirnames, filenames in os.walk(root):
        gpkg = [f for f in filenames if f.lower().endswith('.gpkg')]
        if gpkg:
            rel = os.path.relpath(dirpath, root)
            result[rel] = len(gpkg)
    return result


def find_road_files(root):
    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if not (f.endswith('.gpkg') or f.endswith('.shp')):
                continue
            rel = os.path.join(os.path.relpath(dirpath, root), f)
            score = 0
            if 'merged' in f.lower():
                score += 10
            if f.endswith('.gpkg'):
                score += 3
            elif f.endswith('.shp'):
                score += 2
            result.append((score, rel))
    result.sort(reverse=True)
    return [r[1] for r in result]


def peek_fields(gpkg_path):
    try:
        conn = sqlite3.connect(gpkg_path)
        cur = conn.execute("SELECT table_name FROM gpkg_contents")
        tables = cur.fetchall()
        if not tables:
            conn.close()
            return []
        cur = conn.execute('PRAGMA table_info("' + tables[0][0] + '")')
        cols = [row[1] for row in cur.fetchall()]
        conn.close()
        return cols
    except Exception:
        return []


def run_chainage(
    input_dir, road_path, output_dir,
    base_chainage=None,
    section_field='layer',
    easting_field='UTM 45 X',
    northing_field='UTM 45 Y',
    elevation_field='Ortho Heig',
):
    from qgis.core import QgsVectorLayer

    os.makedirs(output_dir, exist_ok=True)

    road = QgsVectorLayer(road_path, 'road', 'ogr')
    if not road.isValid():
        print("\n[FATAL] Cannot load road:", road_path)
        return

    road_sections = {}
    road_fields = [f.name() for f in road.fields()]
    for feat in road.getFeatures():
        sname = str(feat[section_field]) if section_field in road_fields else 'road'
        geom = feat.geometry()
        if sname in road_sections:
            road_sections[sname] = road_sections[sname].combine(geom)
        else:
            road_sections[sname] = geom

    if not road_sections:
        print("[FATAL] Road layer has no features")
        return

    gpkg_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith('.gpkg'))
    if not gpkg_files:
        print("[WARN] No .gpkg files found in", input_dir)
        return

    print("  Road sections:", list(road_sections.keys()))
    print("  Survey files :", len(gpkg_files))

    for fname in gpkg_files:
        path = os.path.join(input_dir, fname)
        section = os.path.splitext(fname)[0]

        pts = QgsVectorLayer(path, section, 'ogr')
        if not pts.isValid():
            print("  [{}] SKIP (invalid)".format(section))
            continue

        road_geom = None
        for sname, geom in road_sections.items():
            if sname.lower() in section.lower() or section.lower() in sname.lower():
                road_geom = geom
                break
        if road_geom is None:
            road_geom = next(iter(road_sections.values()))

        base = base_chainage.get(section, 0) if base_chainage else 0
        csv_path = os.path.join(output_dir, section + '.csv')
        pt_fields = [f.name() for f in pts.fields()]
        written = 0

        with open(csv_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['Road', 'Chainage', 'Easting', 'Northing', 'Elevation'])
            for feat in pts.getFeatures():
                east = feat[easting_field] if easting_field in pt_fields else None
                north = feat[northing_field] if northing_field in pt_fields else None
                elev = feat[elevation_field] if elevation_field in pt_fields else None
                pt_geom = feat.geometry()
                if road_geom and pt_geom:
                    cv = base + road_geom.lineLocatePoint(pt_geom)
                else:
                    cv = base
                w.writerow([
                    section,
                    '{:.4f}'.format(cv),
                    '{:.3f}'.format(east) if east is not None else '',
                    '{:.3f}'.format(north) if north is not None else '',
                    '{:.3f}'.format(elev) if elev is not None else '',
                ])
                written += 1
        print("  [{}] {} pts -> {}".format(section, written, os.path.basename(csv_path)))

    print("\n[DONE] Results in", output_dir)


def setup(project_dir):
    print()
    print('=' * 60)
    print('  Project:', project_dir)
    print('=' * 60)
    print('  No config found, need to set it up.')

    gpkg_folders = find_gpkg_folders(project_dir)
    if gpkg_folders:
        items = sorted(gpkg_folders.items())
        print('\n  Folders with GPKG files:')
        for i, (folder, count) in enumerate(items, 1):
            print('    [{}] {} ({} files)'.format(i, folder, count))
        print('    [{}] Enter a different path'.format(len(items) + 1))
        while True:
            c = input('  Pick folder [1-{}]: '.format(len(items) + 1)).strip()
            if c.isdigit():
                n = int(c)
                if 1 <= n <= len(items):
                    input_dir = items[n - 1][0]
                    break
                elif n == len(items) + 1:
                    input_dir = input('  Enter survey GPKG folder: ').strip()
                    break
            print('  Invalid.')
    else:
        print('  No GPKG files found anywhere.')
        input_dir = input('  Enter survey GPKG folder: ').strip() or '.'

    full_input = os.path.join(project_dir, input_dir.replace('/', os.sep))
    gpkg_files = sorted(f for f in os.listdir(full_input) if f.endswith('.gpkg'))
    print('\n  Using:', input_dir, '(' + str(len(gpkg_files)) + ' files)')

    road_files = find_road_files(project_dir)
    if road_files:
        print('\n  Road files found:')
        for i, rf in enumerate(road_files, 1):
            print('    [{}] {}'.format(i, rf))
        print('    [{}] Enter a different path'.format(len(road_files) + 1))
        while True:
            c = input('  Pick road file [1-{}]: '.format(len(road_files) + 1)).strip()
            if c.isdigit():
                n = int(c)
                if 1 <= n <= len(road_files):
                    road_path = road_files[n - 1]
                    break
                elif n == len(road_files) + 1:
                    road_path = input('  Enter road centerline path: ').strip()
                    break
            print('  Invalid.')
    else:
        print('  No road files found.')
        road_path = input('  Enter road centerline path: ').strip()

    print('\n  Road:', road_path)

    print('\n  Checking field names from first GPKG...')
    first_gpkg = os.path.join(full_input, gpkg_files[0]) if gpkg_files else None
    detected = peek_fields(first_gpkg) if first_gpkg else []
    if detected:
        print('  Fields found:', detected)
        ef = pick_field(detected, 'Easting', 'UTM 45 X')
        nf = pick_field(detected, 'Northing', 'UTM 45 Y')
        el = pick_field(detected, 'Elevation', 'Ortho Heig')
    else:
        print('  Could not read fields, enter manually.')
        ef = input('  Easting field [UTM 45 X]: ').strip() or 'UTM 45 X'
        nf = input('  Northing field [UTM 45 Y]: ').strip() or 'UTM 45 Y'
        el = input('  Elevation field [Ortho Heig]: ').strip() or 'Ortho Heig'
    sf = input('  Road section field [layer]: ').strip() or 'layer'
    crs = input('  CRS [EPSG:32645]: ').strip() or 'EPSG:32645'

    print('')
    base_chainage = {}
    for f in gpkg_files:
        section = os.path.splitext(f)[0]
        v = input('  Base chainage for {} (Enter=0): '.format(section)).strip()
        base_chainage[section] = float(v) if v else 0.0

    config = {
        'input_dir': input_dir.replace('\\', '/'),
        'road_path': road_path.replace('\\', '/'),
        'output_dir': OUT,
        'section_field': sf,
        'easting_field': ef,
        'northing_field': nf,
        'elevation_field': el,
        'crs': crs,
        'base_chainage': base_chainage,
    }
    config_path = os.path.join(project_dir, CFG)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print('\n  Saved:', config_path)
    return config


def pick_field(fields, label, default):
    print('  {} field:'.format(label))
    for i, f in enumerate(fields, 1):
        m = ' (default)' if f == default else ''
        print('    [{}] {}{}'.format(i, f, m))
    print('    [{}] Type custom'.format(len(fields) + 1))
    while True:
        c = input('  Pick {} [1-{} or Enter for {}]: '.format(label, len(fields), default)).strip()
        if not c:
            return default
        if c.isdigit():
            n = int(c)
            if 1 <= n <= len(fields):
                return fields[n - 1]
            elif n == len(fields) + 1:
                return input('  Enter {} field name: '.format(label)).strip()
        print('  Invalid.')


def load_cfg(project_dir):
    path = os.path.join(project_dir, CFG)
    if os.path.exists(path):
        print('  Config:', path)
        with open(path) as f:
            return json.load(f)
    return setup(project_dir)


def run():
    from qgis.core import QgsApplication
    app = QgsApplication([], False)
    app.setPrefixPath(r'C:\OSGeo4W\apps\qgis-ltr', True)
    app.initQgis()
    sys.path.insert(0, r'C:\OSGeo4W\apps\qgis-ltr\python\plugins')
    return app


def main(project_dir, output_root=None):
    project_dir = os.path.abspath(project_dir)
    if not os.path.isdir(project_dir):
        print('[ERROR] Folder not found:', project_dir)
        return

    config = load_cfg(project_dir)

    input_dir = os.path.join(project_dir, config['input_dir'].replace('/', os.sep))
    road_path = os.path.join(project_dir, config['road_path'].replace('/', os.sep))
    output_dir = os.path.join(project_dir, config.get('output_dir', OUT))
    if output_root:
        output_dir = os.path.join(output_root, os.path.basename(project_dir))

    if not os.path.isdir(input_dir):
        print('[ERROR] Input folder not found:', input_dir)
        return
    if not os.path.exists(road_path):
        print('[ERROR] Road file not found:', road_path)
        return

    print()
    print('=' * 60)
    print('  Running chainage extraction')
    print('  Input  :', input_dir)
    print('  Road   :', road_path)
    print('  Output :', output_dir)
    print('=' * 60)

    qapp = run()
    try:
        run_chainage(
            input_dir=input_dir,
            road_path=road_path,
            output_dir=output_dir,
            base_chainage=config.get('base_chainage'),
            section_field=config['section_field'],
            easting_field=config['easting_field'],
            northing_field=config['northing_field'],
            elevation_field=config['elevation_field'],
        )
    finally:
        from qgis.core import QgsApplication
        QgsApplication.exitQgis()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print('Drag a project folder onto run.bat')
