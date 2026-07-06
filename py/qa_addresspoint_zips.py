import arcpy
import os
import argparse


def load_multicluster_zipcodes(resource_path):
    """Load ZIP -> allowed cluster count mappings from a resource file."""
    mapping = {}
    with open(resource_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            zip_code, cluster_count = parts[0], parts[1]
            mapping[str(zip_code)] = int(cluster_count)
    return mapping


def recreate_file_gdb(parent_dir, gdb_name):
    """Delete and recreate a file geodatabase, returning its full path."""
    gdb_path = os.path.join(parent_dir, gdb_name)
    if arcpy.Exists(gdb_path):
        arcpy.management.Delete(gdb_path)
    arcpy.management.CreateFileGDB(parent_dir, gdb_name)
    return gdb_path

def make_polyline_zip_point_layer(fc
                                 ,scratch_gdb
                                 ,zip_token
                                 ,zip_code
                                 ,where_clause
                                 ,layer_name):

    # Todo: do better
    line_densify_distance = "500 feet" 
    line_end_points = 'END_POINTS'

    # convert centerlines to points                             
    temp_line_layer = f"line_lyr_{zip_token}_{zip_code}"
    if arcpy.Exists(temp_line_layer):
        arcpy.management.Delete(temp_line_layer)

    arcpy.management.MakeFeatureLayer(fc, temp_line_layer, where_clause)

    points_fc = f"{scratch_gdb}/points_{zip_token}_{zip_code}"
    if arcpy.Exists(points_fc):
        arcpy.management.Delete(points_fc)

    # GeneratePointsAlongLines doesnt appear to support named parameters 
    arcpy.management.GeneratePointsAlongLines(
        temp_line_layer,
        points_fc,
        "DISTANCE",
        line_densify_distance,
        None,
        line_end_points
    )

    arcpy.management.MakeFeatureLayer(points_fc, layer_name)

def main():

    parser = argparse.ArgumentParser(description=
                                    "QA addresspoint or centerline ZIP codes")
    parser.add_argument("fc", help="Input CSCL dataset")
    parser.add_argument(
        "--minimum-sample-size",
        type=int,
        default=5,
        help="Minimum point count required for a ZIP to be evaluated (default: 5)",
    )
    parser.add_argument(
        "--neighborhood-radius",
        default="4000 feet",
        help="Neighborhood radius for DBSCAN (default: '4000 feet')",
    )
    parser.add_argument(
        "--minimum-cluster-count",
        type=int,
        default=3,
        help="Minimum features per cluster for DBSCAN (default: 3)",
    )
    args = parser.parse_args()

    resource_dir = os.path.join(os.path.dirname(__file__), "resources")
    scratch_gdb = recreate_file_gdb(resource_dir, "scratch.gdb")
    problem_gdb = recreate_file_gdb(resource_dir, "problem.gdb")

    out_zips = os.path.join(problem_gdb,'problem_zips')

    shape_type = arcpy.Describe(args.fc).shapeType

    minimum_sample_size = args.minimum_sample_size
    neighborhood_radius = args.neighborhood_radius
    minimum_cluster_count = args.minimum_cluster_count

    if shape_type == 'Point':
        zip_fields = ['ZIPCODE']
    elif shape_type == 'Polyline':
        zip_fields = ['L_ZIP'
                     ,'R_ZIP']
    else:
        raise ValueError('input {0} has shape type {1}'.format(args.fc
                                                              ,shape_type))

    multicluster_zip_resource = os.path.join(
        os.path.dirname(__file__), "resources", "multiclusterzipcodes"
    )
    special_zips = load_multicluster_zipcodes(multicluster_zip_resource)

    problem_zips = []

    if shape_type == 'Polyline':
        # Build one ZIP list using both sides, then process each ZIP once.
        zips = sorted({
            value
            for row in arcpy.da.SearchCursor(args.fc, ["L_ZIP", "R_ZIP"])
            for value in row
            if value not in (None, "", " ")
        })
    else:
        zips = sorted({
            row[0] for row in arcpy.da.SearchCursor(args.fc, ["ZIPCODE"])
            if row[0] not in (None, "", " ")
        })

    # override to check selected
    #zips = [11231,11695,11697]

    for z in zips:

        if shape_type == 'Polyline':
            where = f"L_ZIP = '{z}' OR R_ZIP = '{z}'"
            layer_name = f"zip_lyr_LRZIP_{z}"
            zip_token = "LRZIP"
        else:
            where = f"ZIPCODE = '{z}'"
            layer_name = f"zip_lyr_ZIPCODE_{z}"
            zip_token = "ZIPCODE"

        # Delete old layer
        if arcpy.Exists(layer_name):
            arcpy.management.Delete(layer_name)

        # For polylines, generate points along lines
        if shape_type == 'Polyline':
            make_polyline_zip_point_layer(
                args.fc,
                scratch_gdb,
                zip_token,
                z,
                where,
                layer_name
            )
        else:
            # For points, create layer directly with where clause
            arcpy.management.MakeFeatureLayer(args.fc
                                             ,layer_name
                                             ,where)

        # Count points
        count = int(arcpy.management.GetCount(layer_name)[0])

        # skip ZIPs with limited data to evaluate
        if count < minimum_sample_size:
            print(f"Skipping ZIP {z}: only {count} points")
            continue

        # Output FC
        out_fc = f"{scratch_gdb}/cluster_{zip_token}_{z}"

        # Delete old output
        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)

        # this thing is chatty so we add what it is yakking about
        print('{0}: {1}'.format(zip_token, z))
        
        arcpy.stats.DensityBasedClustering(
            layer_name,
            out_fc,
            "DBSCAN",
            minimum_cluster_count,
            neighborhood_radius
        )

        # Count clusters
        cluster_ids = {
            row[0] for row in arcpy.da.SearchCursor(out_fc, ["CLUSTER_ID"])
        }

        allowed_clusters = special_zips.get(z, 1) # default = 1 unless special

        if len(cluster_ids) > allowed_clusters:
            problem_zips.append(z)

    # Create final layer of only problematic ZIPs
    if problem_zips:
        print("Problem ZIPs:", problem_zips)
        zip_list = ",".join([f"'{z}'" for z in problem_zips])
        if shape_type == 'Polyline':
            # For polylines, check both L_ZIP and R_ZIP
            sql = f"({' OR '.join([f'{zf} IN ({zip_list})' for zf in zip_fields])})"
        else:
            # For points, check ZIPCODE
            sql = f"ZIPCODE IN ({zip_list})"
        arcpy.management.MakeFeatureLayer(args.fc, "problem_zip_points", sql)
        arcpy.management.CopyFeatures("problem_zip_points", out_zips)
    else:
        print("No problem zips")

if __name__ == '__main__':
    main()
