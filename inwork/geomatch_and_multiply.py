def geomatch_and_multiply(
    countries_fc, 
    iso_table,
    name_col,
    out_gdb = "country_mult.gdb", 
    countries_join_field = "ISO_CC",
    table_join_field = "country_aor",
    feature_dataset_name = "individual_fc"
):
    
    """
    Description: 
        1) Used to match an ISO3 country coded polygon feature class, with an ISO3 coded table to geolocate table records to the associated polygon.
        2) Split overlapping records within one polygon, to individual feature classes.
        NOTE: Designed for geolocating terrorist organizations from the CIA World Factbook.
    ---
    countries_fc (path):
        path to feature class with country polygons
        (preferred -- coded using the ISO3 standard)
    
    iso_table (path): 
        path to table that will be matched and replicated 
        (preferred -- coded using the ISO3 standard)
        
    name_col (str):
        column of indexed values i.e., 'Name'
        
    out_gdb (str): 
        new gdb name to store the new feature class -- 'name.gdb'
        (default -- 'country_mult.gdb')
        
    countries_join_field (str):
        column name for country fc joining (prefered -- ISO3 code column)
        (default -- "ISO_CC" -- designed for provided country fc)
        
    table_join_field (str):
        column name on table for country fc joining (prefered -- ISO3 code column)
        (default -- "country_aor" -- designed for 'wfb_t_orgs_geolocated' table -- can be used for other datasets but, must input correct column name that matches substituted dataset)
        
    feature_dataset_name (str):
        name of feature dataset that will contain the individually mapped feature classes
        (default -- "individual_fc")
    """
    
    import arcpy
    # Get CURRENT project
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    
    #--------------CHECK FOR GDB-----------------------------
    # Store original gdb file path
    og_default_gdb = aprx.defaultGeodatabase
    
    tf = []
    for d in aprx.databases:
        # If the new gdb is not present...add false to the list
        if not d['databasePath'].endswith(out_gdb):
            tf.append(False)
        else:
            tf.append(True)
    
    if any(x == True for x in tf):
        # Set 'out_gdb' as default to work with
        aprx.defaultGeodatabase = f"{aprx.homeFolder}\\{out_gdb}"
    else:
        # Create new gdb to match the 'out_gdb' parameter
        arcpy.management.CreateFileGDB(aprx.homeFolder, out_gdb)
        # Set newly created gdb as default to work with and add to 'databases' list 
        aprx.defaultGeodatabase = f"{aprx.homeFolder}\\{out_gdb}"
        print(out_gdb + " created!")
    
    #_______________________PART 1___________________________________________________
    # Credit for part 1 goes to AI which helped me design the actual operation of the code. I only adjusted certain portions to integrate it with the whole function.
    mult_fc = f"{aprx.defaultGeodatabase}\\countries_multiplied",

    # Fields to copy from countries (geometry + attributes)
    countries_fields = [f.name for f in arcpy.ListFields(countries_fc) if f.type != 'Geometry']
    
    # Fields to copy from table (attributes only, no geometry)
    table_fields = [f.name for f in arcpy.ListFields(iso_table) if f.type != 'Geometry']
    
    # Full list of output fields (all from countries + all from table)
    output_fields = countries_fields + table_fields + ['SHAPE@']
    
    # Create output feature class, copying schema from countries_fc
    arcpy.CreateFeatureclass_management(
        out_path=aprx.defaultGeodatabase,
        out_name="countries_multiplied",
        geometry_type=arcpy.Describe(countries_fc).shapeType,
        template=countries_fc,
        spatial_reference=arcpy.Describe(countries_fc).spatialReference
    )
    
    # Add fields from the table to mult_fc (if they don’t already exist)
    existing_fields = [f.name for f in arcpy.ListFields("countries_multiplied")]
    for fld in table_fields:
        if fld not in existing_fields:
            field_obj = arcpy.ListFields(iso_table, fld)[0]
            arcpy.AddField_management("countries_multiplied", fld, field_obj.type, 
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
    
    # Now open insert cursor to mult_fc
    with arcpy.da.SearchCursor(countries_fc, countries_fields + ['SHAPE@']) as country_cursor, \
         arcpy.da.InsertCursor("countries_multiplied", output_fields) as insert_cursor:
        for country_row in country_cursor:
            country_code = country_row[countries_fields.index(countries_join_field)]
            if country_code in table_dict:
                for tbl_attrs in table_dict[country_code]:
                    # Combine country and table attributes plus geometry
                    out_row = list(country_row[:-1]) + list(tbl_attrs) + [country_row[-1]]
                    insert_cursor.insertRow(out_row)
                    
    print("Many-to-many replication completed!")
    
    #_______________________PART 2___________________________________________________
    # Stats table to be created - to get unique name count (i.e, index--not record count)
    stats_table = f"{aprx.defaultGeodatabase}\\stats_table"
    
    # Run stats to get count and name of each t_org
    arcpy.analysis.Statistics(iso_table, stats_table, [[name_col, "COUNT"]], case_field=name_col)
    
    # Feature layer "countries_multiplied" must be in map
    mult_lyr = aprx.activeMap.listLayers('countries_multiplied')
    # Get the unique values of each name/index from table and put in list
    names_array = arcpy.da.TableToNumPyArray(stats_table, [name_col])
    
    # Create Feature Dataset named "individual_fc" as a container to store the individual Feature Classes
    arcpy.management.CreateFeatureDataset(
        out_dataset_path=out_gdb,
        out_name=feature_dataset_name
    )
    
    # Run a loop for the entirety of the list
    i = -1
    while i < len(names_array) - 1:
        i = i + 1
        
        # Clean strings to remove forbidden characters
        fc_name = names_array[i][0].replace(" ", "_").replace("'", "_").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_").replace("’", "_").replace("–", "_").replace(",", "")
        
        # Export Feature Class based on matching #s in "Field1" (number associated with the unique value)
        arcpy.conversion.ExportFeatures(
            in_features = "countries_multiplied",
            out_features = f"{out_gdb}\\{feature_dataset_name}\\{fc_name}",
            where_clause = f"Field1 = {i}"
        )
        # Name of newley created layer
        new_lyr = aprx.activeMap.listLayers(fc_name)
        
        # Delete newly created layer to save space in the "Contents" pane
        arcpy.Delete_management(new_lyr)
    
    # ---------------------RETURN GDB TO ORIGINAL DEFAULT------------------------------
    # Set default back to original gdb file path
    aprx.defaultGeodatabase = og_default_gdb

    print('Individual Mapping Complete')
