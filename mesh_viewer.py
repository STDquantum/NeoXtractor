import os  
from typing import Optional  
from PySide6 import QtWidgets, QtCore, QtGui  
  
from core.file import SimpleFile  
from core.mesh_loader.loader import MeshLoader  
from core.mesh_loader.parsers.parser_3 import MeshParser3  
from gui.widgets.viewers.mesh_viewer.viewer_widget import MeshViewer  
from gui.widgets.viewer import Viewer  
  
class MeshFileBrowser(QtWidgets.QMainWindow):  
    """简单的网格文件浏览器界面，集成3D预览"""  
      
    def __init__(self):  
        super().__init__()  
        self.setWindowTitle("网格文件浏览器")  
        self.setMinimumSize(1200, 800)  
          
        # 初始化组件  
        self.mesh_loader = MeshLoader()  
        self.current_folder = None  
        self.mesh_files = []  
          
        self.setup_ui()  
          
    def setup_ui(self):  
        """设置用户界面"""  
        central_widget = QtWidgets.QWidget()  
        self.setCentralWidget(central_widget)  
          
        layout = QtWidgets.QHBoxLayout(central_widget)  
          
        # 左侧控制面板  
        left_panel = QtWidgets.QVBoxLayout()  
          
        # 文件夹选择按钮  
        self.folder_button = QtWidgets.QPushButton("选择文件夹")  
        self.folder_button.clicked.connect(self.select_folder)  
        left_panel.addWidget(self.folder_button)  
          
        # 当前文件夹标签  
        self.folder_label = QtWidgets.QLabel("未选择文件夹")  
        self.folder_label.setWordWrap(True)  
        left_panel.addWidget(self.folder_label)  
          
        # 文件列表  
        self.file_list = QtWidgets.QListWidget()  
        self.file_list.itemClicked.connect(self.on_file_selected)  
        left_panel.addWidget(self.file_list)  
          
        # 右侧预览面板 - 使用垂直分割器  
        right_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)  
          
        # 3D网格查看器  
        self.mesh_viewer = MeshViewer()  
        right_splitter.addWidget(self.mesh_viewer)  
          
        # 文件信息面板  
        info_widget = QtWidgets.QWidget()  
        info_layout = QtWidgets.QVBoxLayout(info_widget)  
          
        info_label = QtWidgets.QLabel("文件信息")  
        info_label.setStyleSheet("font-weight: bold; font-size: 14px;")  
        info_layout.addWidget(info_label)  
          
        self.info_text = QtWidgets.QTextEdit()  
        self.info_text.setReadOnly(True)  
        self.info_text.setMaximumHeight(200)  
        info_layout.addWidget(self.info_text)  
          
        right_splitter.addWidget(info_widget)  
          
        # 设置分割器比例 (3D查看器占大部分空间)  
        right_splitter.setSizes([600, 200])  
          
        # 添加到主布局  
        left_widget = QtWidgets.QWidget()  
        left_widget.setLayout(left_panel)  
        left_widget.setMaximumWidth(350)  
          
        layout.addWidget(left_widget)  
        layout.addWidget(right_splitter)  
          
        # 设置主布局比例  
        layout.setStretch(0, 1)  # 左侧面板  
        layout.setStretch(1, 3)  # 右侧预览面板  
          
    def select_folder(self):  
        """选择包含.mesh文件的文件夹"""  
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(  
            self,  
            "选择包含 .mesh 文件的文件夹",  
            ""  
        )  
        if folder_path:  
            self.current_folder = folder_path  
            self.folder_label.setText(f"当前文件夹: {folder_path}")  
            self.load_mesh_files(folder_path)  
      
    def load_mesh_files(self, folder_path: str):  
        """加载文件夹中的.mesh文件并按大小排序"""  
        self.mesh_files = []  
        self.file_list.clear()  
          
        try:  
            for filename in os.listdir(folder_path):  
                if filename.lower().endswith('.mesh'):  
                    file_path = os.path.join(folder_path, filename)  
                    file_size = os.path.getsize(file_path)  
                    self.mesh_files.append((filename, file_path, file_size))  
              
            # 按文件大小排序  
            self.mesh_files.sort(key=lambda x: x[2])  
              
            # 填充文件列表  
            for filename, file_path, file_size in self.mesh_files:  
                size_str = self.format_file_size(file_size)  
                item_text = f"{filename} ({size_str})"  
                item = QtWidgets.QListWidgetItem(item_text)  
                item.setData(QtCore.Qt.ItemDataRole.UserRole, file_path)  
                self.file_list.addItem(item)  
                  
        except Exception as e:  
            QtWidgets.QMessageBox.warning(  
                self,  
                "错误",  
                f"加载文件夹失败: {str(e)}"  
            )  
      
    def format_file_size(self, size_bytes: int) -> str:  
        """格式化文件大小显示"""  
        if size_bytes < 1024:  
            return f"{size_bytes} B"  
        elif size_bytes < 1024 * 1024:  
            return f"{size_bytes / 1024:.1f} KB"  
        else:  
            return f"{size_bytes / (1024 * 1024):.1f} MB"  
      
    def on_file_selected(self, item: QtWidgets.QListWidgetItem):  
        """文件被选中时的处理"""  
        file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)  
        self.load_and_preview_mesh(file_path)  
      
    def load_and_preview_mesh(self, file_path: str):  
        """加载并预览网格文件"""  
        try:  
            # 读取文件数据  
            with open(file_path, 'rb') as f:  
                data = f.read()  
              
            # 创建文件对象并加载到3D查看器  
            filename = os.path.basename(file_path)  
            file_obj = SimpleFile(filename, data)  
              
            # 直接在嵌入的查看器中加载文件  
            self.mesh_viewer.set_file(file_obj)  
              
            # 使用MeshParser3解析文件信息  
            parser = MeshParser3()  
            mesh_data = parser.parse(data)  
              
            # 显示文件信息  
            info_text = self.format_mesh_info(mesh_data, file_path)  
            self.info_text.setPlainText(info_text)  
              
        except Exception as e:  
            error_text = f"加载文件失败: {str(e)}\n\n文件路径: {file_path}"  
            self.info_text.setPlainText(error_text)  
            # 清空3D查看器  
            self.mesh_viewer.unload_file()  
      
    def format_mesh_info(self, mesh_data, file_path: str) -> str:  
        """格式化网格信息显示"""  
        info_lines = [  
            f"文件路径: {file_path}",  
            f"文件大小: {self.format_file_size(os.path.getsize(file_path))}",  
            "",  
            "=== 网格信息 ===",  
            f"版本: {mesh_data.version}",  
            f"顶点数量: {len(mesh_data.position)}",  
            f"面数量: {len(mesh_data.face)}",  
            f"UV坐标数量: {len(mesh_data.uv)}",  
            f"法线数量: {len(mesh_data.normal)}",  
            "",  
            f"包含骨骼: {'是' if mesh_data.bone_exist else '否'}",  
        ]  
          
        if mesh_data.bone_exist:  
            info_lines.extend([  
                f"骨骼数量: {len(mesh_data.bone_name)}",  
                f"骨骼名称: {', '.join(mesh_data.bone_name[:5])}{'...' if len(mesh_data.bone_name) > 5 else ''}",  
            ])  
          
        return "\n".join(info_lines)  
  
def main():  
    """主函数"""  
    import sys  
    app = QtWidgets.QApplication(sys.argv)  
      
    browser = MeshFileBrowser()  
    browser.show()  
      
    sys.exit(app.exec())  
  
if __name__ == "__main__":  
    main()