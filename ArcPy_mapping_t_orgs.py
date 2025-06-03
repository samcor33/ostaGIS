# 1) Create Overlapping Organization Feature Class

# All credit for this code goes to ChatGPT

import arcpy

# Inputs
countries_fc = r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\t_orgs_aor.gdb\test"
iso_table = r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\Worlwide_Threat_Analysis.gdb\wfb_t_orgs_geolocated"
output_fc = r"C:\GIS\ArcGIS\Projects\Worlwide_Threat_Analysis\t_orgs_aor.gdb\countries_multiplied"

# Fields to join on
countries_join_field = "ISO_CC"
table_join_field = "country_aor"

# Fields to copy from countries (geometry + attributes)
countries_fields = [f.name for f in arcpy.ListFields(countries_fc) if f.type != 'Geometry']

# Fields to copy from table (attributes only, no geometry)
table_fields = [f.name for f in arcpy.ListFields(iso_table) if f.type != 'Geometry']

# Full list of output fields (all from countries + all from table)
output_fields = countries_fields + table_fields + ['SHAPE@']

# Create output feature class, copying schema from countries_fc
arcpy.CreateFeatureclass_management(
    out_path=arcpy.env.workspace,
    out_name="countries_multiplied",#arcpy.Describe(output_fc).name,
    geometry_type=arcpy.Describe(countries_fc).shapeType,
    template=countries_fc,
    spatial_reference=arcpy.Describe(countries_fc).spatialReference
)

# Add fields from the table to output_fc (if they don’t already exist)
existing_fields = [f.name for f in arcpy.ListFields(output_fc)]
for fld in table_fields:
    if fld not in existing_fields:
        field_obj = arcpy.ListFields(iso_table, fld)[0]
        arcpy.AddField_management(output_fc, fld, field_obj.type, 
                                  field_obj.precision, field_obj.scale, field_obj.length)

# Build a dict mapping ISO code -> list of table records
table_dict = {}
with arcpy.da.SearchCursor(iso_table, table_fields + [table_join_field]) as cursor:
    for row in cursor:
        # last field is the join key value
        join_val = row[-1]
        if join_val is None:
            continue
        rec_attrs = row[:-1]  # all other fields
        table_dict.setdefault(join_val, []).append(rec_attrs)

# Now open insert cursor to output_fc
with arcpy.da.SearchCursor(countries_fc, countries_fields + ['SHAPE@']) as country_cursor, \
     arcpy.da.InsertCursor(output_fc, output_fields) as insert_cursor:
    for country_row in country_cursor:
        country_code = country_row[countries_fields.index(countries_join_field)]
        if country_code in table_dict:
            for tbl_attrs in table_dict[country_code]:
                # Combine country and table attributes plus geometry
                out_row = list(country_row[:-1]) + list(tbl_attrs) + [country_row[-1]]
                insert_cursor.insertRow(out_row)

print("Many-to-many replication completed!")



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



# 3) Apply style to all layers in group

aprx = arcpy.mp.ArcGISProject("CURRENT")

# get the current map
m = aprx.activeMap

# individual org layers must be grouped as "t_org_individual"
# find all layers in map
lyrs = m.listLayers()

# find the grouped layers in group "t_org_individual"
for gp_lyr in lyrs:
    if gp_lyr.name == "t_org_individual":
        gpd_lyrs = gp_lyr.listLayers()
        
        # run loop counting the total of layers in the group
        i = -1
        while i < len(gpd_lyrs) -1 :
            i = i + 1
            
            # get the symbology for each layer
            symbology = gpd_lyrs[i].symbology

            if hasattr(symbology, "renderer"):
                symbology.updateRenderer("SimpleRenderer")
            # update symbology to style named "t_org_aor"
                symbology.renderer.symbol.applySymbolFromGallery("t_org_aor")
                gpd_lyrs[i].symbology = symbology  # Apply changes

print('Mapping Complete')
