import subprocess
import os
from PIL import Image

#before program starting you need to install FLIF software from https://github.com/FLIF-hub/FLIF
flif_converter_path = 'C:/Users/yuddim/Downloads/FLIF-master/build/MSVC/flif'
decode_flag = '-d'
source_path = 'D:/Projects/icevision/data'
target_path = 'D:/Projects/icevision/data_jpg'


def convert_file_flif_to_jpg(flif_converter_path, decode_flag, source_path,
                             target_path, source_file_name, quality_level):
    source_full_path = source_path + '/'+source_file_name
    file_name_no_ext = source_file_name.split('.')
    target_file_name = file_name_no_ext[0]+'_32bit.png'

    target_full_path = target_path+'/'+target_file_name

    subprocess.run([flif_converter_path, decode_flag, source_full_path, target_full_path])

    #png analyze and convert to 24 bit jpeg
    img = Image.open(target_full_path)
    img_type = img.mode #it will be RGBA mode
    img_width = img.size[0]
    rgb_image = img.convert('RGB')
    if(img_width>1000): #if image is smaller than we have error in conversion
        new_target_full_path = target_path+'/'+file_name_no_ext[0]+'.jpg'
        rgb_image.save(new_target_full_path, format='JPEG', subsampling=0, quality=quality_level)

    os.remove(target_full_path)


def convert_path_flif_to_jpg(flif_converter_path, decode_flag, source_path, target_path, quality_level):
    os.makedirs(target_path, exist_ok=True)
    flif_file_list = os.listdir(source_path)
    for id, flif_file_name in enumerate(flif_file_list):
        convert_file_flif_to_jpg(flif_converter_path=flif_converter_path,
                                 decode_flag=decode_flag,
                                 source_path=source_path,
                                 target_path=target_path,
                                 source_file_name=flif_file_name,
                                 quality_level=quality_level)
        print('Image ' + str(id) + ': ' + flif_file_name)

convert_path_flif_to_jpg(flif_converter_path=flif_converter_path,
                         decode_flag=decode_flag,
                         source_path=source_path,
                         target_path=target_path,
                         quality_level=85)