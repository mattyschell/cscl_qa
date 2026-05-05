import arcpy
import os
import argparse

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
    parser.add_argument("scratch_gdb", help="Scratch geodatabase")
    parser.add_argument("problem_gdb", help="Output baddie geodatabase")
    args = parser.parse_args()

    out_zips = os.path.join(args.problem_gdb,'problem_zips')

    shape_type = arcpy.Describe(args.fc).shapeType

    # todo: review
    # entering the hard code zone
    minimum_sample_size = 5
    neighborhood_radius = "4000 feet"
    minimum_cluster_count = 3

    if shape_type == 'Point':
        zip_fields = ['ZIPCODE']
    elif shape_type == 'Polyline':
        zip_fields = ['L_ZIP'
                     ,'R_ZIP']
    else:
        raise ValueError('input {0} has shape type {1}'.format(args.fc
                                                              ,shape_type))

    # ZIP codes we know to be in 2 clusters 
    special_zips = {
        "10004": 2,
        "10121": 2,
        "10155": 2,
        "11370": 2,
        "10464": 2,
        "11695": 2,
        "11697": 2
    }   
    # exiting the hard code zone

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
                args.scratch_gdb,
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
        out_fc = f"{args.scratch_gdb}/cluster_{zip_token}_{z}"

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
