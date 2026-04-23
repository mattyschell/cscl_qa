import arcpy
import os
import argparse

def main():

    parser = argparse.ArgumentParser(description="QA addresspoint ZIP codes")
    parser.add_argument("fc", help="Input address point dataset")
    parser.add_argument("scratch_gdb", help="Input scratch geodatabase")
    parser.add_argument("problem_gdb", help="Output baddie geodatabase")
    args = parser.parse_args()

    ignore_zips = {"10004" 
                  ,"11370"}  

    problem_zipz = os.path.join(args.problem_gdb,'problem_zips')
    zip_field    = 'ZIPCODE'

    problem_zips = []

    # Get distinct ZIP codes (skip NULLs)
    zips = sorted({
        row[0] for row in arcpy.da.SearchCursor(args.fc, [zip_field])
        if row[0] not in (None, "", " ")
    })

    for z in zips:

        if z in ignore_zips:
            print(f"Skipping ZIP {z}: in ignore list")
            continue

        where = f"{zip_field} = '{z}'"

        # Unique layer name
        layer_name = f"zip_lyr_{z}"

        # Delete old layer
        if arcpy.Exists(layer_name):
            arcpy.management.Delete(layer_name)

        arcpy.management.MakeFeatureLayer(args.fc, layer_name, where)

        # Count points
        count = int(arcpy.management.GetCount(layer_name)[0])

        # Optional: skip very small ZIPs
        if count < 10:
            print(f"Skipping ZIP {z}: only {count} points")
            continue

        # Output FC
        out_fc = f"{args.scratch_gdb}/cluster_{z}"

        # Delete old output
        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)

        arcpy.stats.DensityBasedClustering(
            layer_name,
            out_fc,
            "DBSCAN",
            3,
            "4000 feet"
        )

        # Count clusters
        cluster_ids = {
            row[0] for row in arcpy.da.SearchCursor(out_fc, ["CLUSTER_ID"])
        }

        if len(cluster_ids) > 1:
            problem_zips.append(z)

    print("Problem ZIPs:", problem_zips)

    # Create final layer of only problematic ZIPs
    if problem_zips:
        zip_list = ",".join([f"'{z}'" for z in problem_zips])
        sql = f"{zip_field} IN ({zip_list})"
        arcpy.management.MakeFeatureLayer(args.fc, "problem_zip_points", sql)
        arcpy.management.CopyFeatures("problem_zip_points", problem_zipz)

if __name__ == '__main__':
    main()