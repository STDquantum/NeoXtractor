import os  
import glob  
from core.npk.npk_file import NPKFile  
from core.npk.class_types import NPKReadOptions, NPKEntryDataFlags  
  
def search_text_in_npk_files(root_dir: str, search_text: str):  
    # 递归查找所有NPK文件  
    npk_files = glob.glob(os.path.join(root_dir, "**/*.npk"), recursive=True)  
    f = open("hastext.txt", "w", encoding="utf-8")
    for npk_path in npk_files:  
        print(f"正在处理文件: {npk_path}")
        try:  
            # 使用适当的配置加载NPK文件  
            read_options = NPKReadOptions(-250)  # 根据HPMA配置调整  
            npk_file = NPKFile(npk_path, read_options)  
              
            # 遍历所有条目  
            for i in range(npk_file.file_count):  
                entry = npk_file.read_entry(i)  
                # 检查是否为文本文件  
                if 1:  
                    f.write(f"{npk_path} -> {entry.filename}\n")
                    try:  
                        text_content = entry.data.decode('utf-8', errors='ignore')  
                        if search_text in text_content:  
                            print(f"找到文本 '{search_text}' 在文件: {npk_path} -> {entry.filename}")  
                            with open("text.txt", "a", encoding="utf-8") as tf:
                                tf.write(text_content)
                    except:  
                        continue  
                          
        except Exception as e:  
            print(f"处理文件 {npk_path} 时出错: {e}")
            
search_text_in_npk_files(r"E:\download\111\com.netease.harrypotter\files\Netease\harrypotter\Documents", "昏昏倒地")