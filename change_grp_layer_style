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
