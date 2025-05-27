#2) Take all combined AORs and split them into separate feature classes by "t_org"

# Get table with t_orgs and ISO3 codes
iso_table = r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\Worlwide_Threat_Analysis.gdb\wfb_t_orgs_geolocated"
# Name of tabel to be created
out_tab = r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\Worlwide_Threat_Analysis.gdb\t_orgs_aor_count"
# Run states to get count and name of each t_org
arcpy.analysis.Statistics(iso_table, out_tab, [["index", "COUNT"]], case_field='index')

aprx = arcpy.mp.ArcGISProject("CURRENT")

# Get fc with combined t_org AORs...and...t_org count table
mult_fc = r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\t_orgs_aor.gdb\countries_multiplied"
t_orgs_table = r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\Worlwide_Threat_Analysis.gdb\t_orgs_aor_count"

# Feature layer "countries_multiplied" must be in map
mult_lyr = aprx.activeMap.listLayers('countries_multiplied')
# Get the names of each t_org from table and put in list
t_os_names_arr = arcpy.da.TableToNumPyArray(t_orgs_table, ['index'])

# Create Feature Dataset named "t_org_individual" to store the individual Feature Classes
arcpy.management.CreateFeatureDataset(
    out_dataset_path=r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\t_orgs_aor.gdb",
    out_name="t_org_individual"
)

# Run a loop for the entirety of the list of t_orgs
i = -1
while i < len(t_os_names_arr) - 1:
    i = i + 1
    
    # Clean t_org strs to remove forbidden characters
    fc_name = t_os_names_arr[i][0].replace(" ", "_").replace("'", "_").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_").replace("’", "_").replace("–", "_").replace(",", "")
    
    # Export Feature Class based on matching #s in "Field1" (number associated with the t_org name)
    arcpy.conversion.ExportFeatures(
        in_features = mult_fc,
        out_features = f"C:\\GIS\ArcGIS\\Projects\\Worlwide_Threat_Analysis\\t_orgs_aor.gdb\\t_org_individual\\{fc_name}",
        where_clause = f"Field1 = {i}"
    )
    # Name of newley created layer
    new_lyr = aprx.activeMap.listLayers(fc_name)
    
    # Delete newly created layer to save space in the "Contents" pane
    arcpy.Delete_management(new_lyr)

print('Mapping Complete')
