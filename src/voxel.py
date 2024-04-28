import src.animation as animation


tile = 30


TILE_FILENAMES = [
    "Art/peacle.png",
    "Art/iso_birchbirch.png",            
    "Art/iso_cobblecobble.png",          
    "Art/iso_cobblecobbleslabslab.png",  
    "Art/iso_dirtdirt.png",              
    "Art/iso_flowerflower1.png",         
    "Art/iso_flowerflower2.png",         
    "Art/iso_flowerflower3.png",         
    "Art/iso_flowerflower4.png",         
    "Art/iso_flowerflower5.png",         
    "Art/iso_flowerflower6.png",         
    "Art/iso_goldgold.png",              
    "Art/iso_grassgrassemptyempty.png",  
    "Art/iso_grassgrass.png",            
    "Art/iso_grassgrassredred.png",      
    "Art/iso_grassgrasssnowsnow.png",    
    "Art/iso_grassgrassyellowyellow.png",
    "Art/iso_hayhay.png",                
    "Art/iso_lavalava.png",              
    "Art/iso_leafleafoldold.png",        
    "Art/iso_leafleaforangeorange.png",  
    "Art/iso_leafleafpinkpink.png",      
    "Art/iso_leafleaf.png",                  
    "Art/iso_leafleafroserose.png",      
    "Art/iso_leafleafwhitewhite.png",    
    "Art/iso_leafleafyellowyellow.png",  
    "Art/iso_mossmoss.png",              
    "Art/iso_redstoneredstonemossmoss.png",
    "Art/iso_redstoneredstone.png",
    "Art/iso_redstoneredstoneslabslab.png",      
    "Art/iso_sandsand.png",              
    "Art/iso_shadowsshadow.png",         
    "Art/iso_snowsnow.png",              
    "Art/iso_stonestone_emptyempty.png", 
    "Art/iso_stonestone.png",            
    "Art/iso_waterwater",
    "Art/iso_waterwaterfullfull",            
    "Art/iso_woodwoodplanksplanks.png",  
    "Art/iso_woodwood.png",
    "Art/iso_grassgrassslabslab.png",
    "Art/iso_grassgrassyellowyellowslabslab.png",
    "Art/iso_woodwoodslabslab.png",
    "Art/iso_sandsandslabslab.png",
    "Art/iso_carbord.png",
    "Art/peacle_heavy.png"]



TILE_TEXTURES = [animation.Animation.from_file(i, (tile,tile), 4) if len(i.split(".")) > 1
                 else animation.Animation.from_dir(i, (tile, tile), 4)
                     for i in TILE_FILENAMES]

iso_tile_scale = 2

iso_tile = iso_tile_scale*tile


ISO_TEXTURES = [animation.Animation.from_file(i, (iso_tile,iso_tile), 4) if len(i.split(".")) > 1
                 else animation.Animation.from_dir(i, (iso_tile, iso_tile), 4)
                     for i in TILE_FILENAMES]


def v3_add(v, w): 
    return (v[0] + w[0], v[1] + w[1], v[2] + w[2])

class Voxel:
    is_player = False #magic nothing wrong here
    def __init__(self, pos, voxel_id):
        self.pos      = pos
        self.voxel_id = voxel_id

    def as_dict(self):
        return {"pos": self.pos, "voxel_id": self.voxel_id}
        
    @property
    def texture(self):
        return TILE_TEXTURES[self.voxel_id - 1].texture

    @property
    def iso_texture(self):
        return ISO_TEXTURES[self.voxel_id - 1].texture


