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
