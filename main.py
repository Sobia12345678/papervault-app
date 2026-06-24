from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
import os
import shutil
from datetime import datetime

# Set app colors
Window.clearcolor = (0.9, 0.92, 0.95, 1)


# ============================================
# Custom FileChooser with Better Visibility
# ============================================
class StyledFileChooser(FileChooserListView):
    """File chooser with styled entries"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_color = (0, 0, 0, 1)
        self.entry_font_size = '16sp'
    
    def _add_file(self, f, **kwargs):
        try:
            if os.path.exists(f) and os.access(f, os.R_OK):
                super()._add_file(f, **kwargs)
        except (PermissionError, OSError, WindowsError, AttributeError):
            pass
    
    def is_hidden(self, fn):
        try:
            return super().is_hidden(fn)
        except Exception:
            return False


# ============================================
# Screen 1: Main Menu / Home Screen
# ============================================
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_folder = None
        self.base_folder = None
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint=(1, 0.2), spacing=10)
        header.add_widget(Label(
            text='📚 PaperVault',
            font_size=45,
            bold=True,
            color=(0.05, 0.15, 0.4, 1)
        ))
        layout.add_widget(header)
        
        # Show current location
        self.location_label = Label(
            text='📍 Location: Not selected',
            font_size=16,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.08)
        )
        layout.add_widget(self.location_label)
        
        # Create Folder Button
        create_btn = Button(
            text='📂 Create Folder',
            font_size=28,
            background_color=(0.15, 0.6, 0.25, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.15)
        )
        create_btn.bind(on_press=self.go_to_create_folder)
        layout.add_widget(create_btn)
        
        # View Files Button
        view_btn = Button(
            text='📄 View Files',
            font_size=28,
            background_color=(0.15, 0.4, 0.7, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.15)
        )
        view_btn.bind(on_press=self.go_to_view_files)
        layout.add_widget(view_btn)
        
        # Status label
        self.status_label = Label(
            text='✅ Ready',
            font_size=16,
            color=(0.1, 0.5, 0.1, 1),
            size_hint=(1, 0.05)
        )
        layout.add_widget(self.status_label)
        
        # Footer
        footer = Label(
            text='PaperVault v1.0 | Manage your test papers',
            font_size=14,
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(1, 0.05)
        )
        layout.add_widget(footer)
        
        self.add_widget(layout)
    
    def go_to_create_folder(self, instance):
        if not self.base_folder:
            self.select_base_folder('create')
        else:
            self.manager.current = 'create_folder'
    
    def go_to_view_files(self, instance):
        if not self.base_folder:
            self.select_base_folder('view')
        else:
            view_screen = self.manager.get_screen('view_files')
            view_screen.current_path = self.base_folder
            view_screen.show_only_folders = True  # Only show folders first
            view_screen.refresh_files(None)
            self.manager.current = 'view_files'
    
    def select_base_folder(self, action='create'):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        user_path = os.path.expanduser('~')
        documents_path = os.path.join(user_path, 'Documents')
        start_path = documents_path if os.path.exists(documents_path) else user_path
        
        filechooser = StyledFileChooser(
            path=start_path,
            dirselect=True,
            size_hint=(1, 0.85)
        )
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        select_btn = Button(
            text='✅ Select Folder',
            background_color=(0.15, 0.6, 0.25, 1),
            color=(1, 1, 1, 1)
        )
        cancel_btn = Button(
            text='❌ Cancel',
            background_color=(0.4, 0.4, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Select Base Folder for Papers',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def select(btn):
            if filechooser.selection:
                self.base_folder = filechooser.selection[0]
                self.current_folder = self.base_folder
                self.location_label.text = f'📍 Location: {self.base_folder}'
                self.status_label.text = f'✅ Base folder selected: {os.path.basename(self.base_folder)}'
                popup.dismiss()
                if action == 'create':
                    self.manager.current = 'create_folder'
                elif action == 'view':
                    view_screen = self.manager.get_screen('view_files')
                    view_screen.current_path = self.base_folder
                    view_screen.show_only_folders = True
                    view_screen.refresh_files(None)
                    self.manager.current = 'view_files'
            else:
                self.status_label.text = '⚠️ Please select a folder'
        
        def cancel(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=select)
        cancel_btn.bind(on_press=cancel)
        
        popup.open()


# ============================================
# Screen 2: Create Folder Screen
# ============================================
class CreateFolderScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(
            text='📂 Create New Folder',
            font_size=30,
            bold=True,
            color=(0.05, 0.15, 0.4, 1),
            size_hint=(1, 0.12)
        ))
        
        self.location_label = Label(
            text='📍 Creating in: Not selected',
            font_size=18,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.location_label)
        
        layout.add_widget(Label(
            text='📝 Enter folder name:',
            font_size=20,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.08)
        ))
        self.folder_input = TextInput(
            text='',
            hint_text='Type folder name...',
            multiline=False,
            font_size=22,
            size_hint=(1, 0.12),
            foreground_color=(0.1, 0.1, 0.1, 1),
            background_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.folder_input)
        
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        
        create_btn = Button(
            text='✅ Create & Open',
            background_color=(0.15, 0.6, 0.25, 1),
            color=(1, 1, 1, 1)
        )
        create_btn.bind(on_press=self.create_folder)
        btn_layout.add_widget(create_btn)
        
        change_location_btn = Button(
            text='📁 Change Location',
            background_color=(0.4, 0.4, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        change_location_btn.bind(on_press=self.change_location)
        btn_layout.add_widget(change_location_btn)
        
        back_btn = Button(
            text='🔙 Back',
            background_color=(0.6, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(back_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_enter(self):
        home_screen = self.manager.get_screen('home')
        if home_screen.base_folder:
            self.location_label.text = f'📍 Creating in: {home_screen.base_folder}'
        else:
            self.location_label.text = '⚠️ No location selected! Click "Change Location"'
    
    def change_location(self, instance):
        home_screen = self.manager.get_screen('home')
        home_screen.select_base_folder('create')
    
    def create_folder(self, instance):
        home_screen = self.manager.get_screen('home')
        
        if not home_screen.base_folder:
            self.show_error_popup('Please select a location first!\nClick "Change Location" button.')
            return
        
        folder_name = self.folder_input.text.strip()
        if not folder_name:
            self.show_error_popup('Please enter a folder name!')
            return
        
        folder_path = os.path.join(home_screen.base_folder, folder_name)
        
        if os.path.exists(folder_path):
            self.show_error_popup(f'Folder "{folder_name}" already exists!\nPlease choose a different name.')
            return
        
        try:
            os.makedirs(folder_path, exist_ok=True)
            home_screen.current_folder = folder_path
            home_screen.location_label.text = f'📍 Location: {folder_path}'
            self.show_success_and_navigate(folder_name, folder_path)
            
        except Exception as e:
            self.show_error_popup(f'Error creating folder: {str(e)}')
    
    def show_success_and_navigate(self, folder_name, folder_path):
        popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        popup_content.add_widget(Label(
            text=f'✅ Folder "{folder_name}" created successfully!\n\n📂 Location: {folder_path}',
            font_size=16,
            color=(0.1, 0.5, 0.1, 1)
        ))
        
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.3))
        
        view_btn = Button(
            text='📄 View Files',
            background_color=(0.15, 0.4, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        upload_btn = Button(
            text='📤 Upload Files',
            background_color=(0.7, 0.35, 0.15, 1),
            color=(1, 1, 1, 1)
        )
        
        btn_layout.add_widget(view_btn)
        btn_layout.add_widget(upload_btn)
        popup_content.add_widget(btn_layout)
        
        popup = Popup(
            title='✅ Success',
            content=popup_content,
            size_hint=(0.85, 0.5)
        )
        
        def on_view(btn):
            popup.dismiss()
            view_screen = self.manager.get_screen('view_files')
            view_screen.current_path = folder_path
            view_screen.show_only_folders = False  # Show files inside
            view_screen.refresh_files(None)
            self.manager.current = 'view_files'
        
        def on_upload(btn):
            popup.dismiss()
            home_screen = self.manager.get_screen('home')
            upload_screen = self.manager.get_screen('upload')
            upload_screen.current_folder = folder_path
            upload_screen.folder_label.text = f'📁 Uploading to: {folder_path}'
            self.manager.current = 'upload'
        
        view_btn.bind(on_press=on_view)
        upload_btn.bind(on_press=on_upload)
        popup.open()
    
    def show_error_popup(self, message):
        popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        popup_content.add_widget(Label(
            text=message,
            font_size=16,
            color=(0.8, 0.2, 0.2, 1)
        ))
        close_btn = Button(text='OK', size_hint=(1, 0.3))
        popup_content.add_widget(close_btn)
        
        popup = Popup(
            title='Error',
            content=popup_content,
            size_hint=(0.8, 0.4)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'home'


# ============================================
# Screen 3: Upload Screen with Progress Bar
# ============================================
class UploadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_folder = None
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint=(1, 0.08), spacing=10)
        header.add_widget(Label(
            text='📤 Upload Files',
            font_size=28,
            bold=True,
            color=(0.05, 0.15, 0.4, 1)
        ))
        layout.add_widget(header)
        
        # Show current folder
        self.folder_label = Label(
            text='📁 No folder selected',
            font_size=16,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.05)
        )
        layout.add_widget(self.folder_label)
        
        # Progress Bar
        self.progress_label = Label(
            text='Progress: 0%',
            font_size=16,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.05)
        )
        layout.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 0.05)
        )
        layout.add_widget(self.progress_bar)
        
        # File chooser
        user_path = os.path.expanduser('~')
        documents_path = os.path.join(user_path, 'Documents')
        start_path = documents_path if os.path.exists(documents_path) else user_path
        
        self.filechooser = StyledFileChooser(
            path=start_path,
            dirselect=False,
            size_hint=(1, 0.62)
        )
        layout.add_widget(self.filechooser)
        
        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        upload_btn = Button(
            text='📤 Upload & Convert to PDF',
            background_color=(0.7, 0.35, 0.15, 1),
            color=(1, 1, 1, 1)
        )
        upload_btn.bind(on_press=self.upload_file)
        btn_layout.add_widget(upload_btn)
        
        back_btn = Button(
            text='🔙 Back',
            background_color=(0.4, 0.4, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(back_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_enter(self):
        if self.current_folder:
            self.folder_label.text = f'📁 Uploading to: {self.current_folder}'
        else:
            home_screen = self.manager.get_screen('home')
            if home_screen.current_folder:
                self.current_folder = home_screen.current_folder
                self.folder_label.text = f'📁 Uploading to: {self.current_folder}'
        # Reset progress
        self.progress_bar.value = 0
        self.progress_label.text = 'Progress: 0%'
    
    def upload_file(self, instance):
        if not self.filechooser.selection:
            self.show_error_popup('Please select a file first!')
            return
        
        if not self.current_folder:
            self.show_error_popup('No folder selected!')
            return
        
        source_file = self.filechooser.selection[0]
        self.convert_to_pdf(source_file, self.current_folder)
    
    def update_progress(self, value, message=""):
        """Update progress bar"""
        self.progress_bar.value = value
        self.progress_label.text = f'Progress: {int(value)}%'
        if message:
            self.progress_label.text = f'{message} - {int(value)}%'
    
    def convert_to_pdf(self, source_file, dest_folder):
        try:
            base_name = os.path.basename(source_file)
            name_without_ext = os.path.splitext(base_name)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_name = f"{name_without_ext}_{timestamp}.pdf"
            pdf_path = os.path.join(dest_folder, pdf_name)
            
            # Get file size for progress
            file_size = os.path.getsize(source_file)
            copied_size = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            # Update progress - Starting
            self.update_progress(10, "Starting upload...")
            
            # Check if file is PDF
            if source_file.lower().endswith('.pdf'):
                self.update_progress(30, "Copying PDF...")
                # Copy with progress
                with open(source_file, 'rb') as src, open(pdf_path, 'wb') as dst:
                    while True:
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        copied_size += len(chunk)
                        progress = min(90, 30 + (copied_size / file_size) * 60)
                        self.update_progress(progress, "Copying PDF...")
                
                self.update_progress(100, "✅ PDF saved!")
                self.show_success_popup(f'✅ PDF saved in: {os.path.basename(dest_folder)}')
                return
            
            # For Word documents
            if source_file.lower().endswith(('.docx', '.doc')):
                self.update_progress(30, "Converting Word to PDF...")
                try:
                    from docx2pdf import convert
                    convert(source_file, pdf_path)
                    self.update_progress(100, "✅ Word converted to PDF!")
                    self.show_success_popup(f'✅ Word document converted and saved in: {os.path.basename(dest_folder)}')
                    return
                except ImportError:
                    # Copy with progress
                    self.update_progress(30, "Copying file...")
                    with open(source_file, 'rb') as src, open(pdf_path, 'wb') as dst:
                        while True:
                            chunk = src.read(chunk_size)
                            if not chunk:
                                break
                            dst.write(chunk)
                            copied_size += len(chunk)
                            progress = min(90, 30 + (copied_size / file_size) * 60)
                            self.update_progress(progress, "Copying file...")
                    
                    self.update_progress(100, "⚠️ File copied (conversion unavailable)")
                    self.show_success_popup(f'⚠️ Word document copied (conversion unavailable)')
                    return
            
            # For text files
            if source_file.lower().endswith('.txt'):
                self.update_progress(30, "Converting Text to PDF...")
                try:
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter
                    from reportlab.lib.units import inch
                    
                    # Read text file
                    with open(source_file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    # Create PDF
                    c = canvas.Canvas(pdf_path, pagesize=letter)
                    width, height = letter
                    
                    y = height - inch
                    lines = text.split('\n')
                    total_lines = len(lines)
                    
                    for i, line in enumerate(lines):
                        if y < inch:
                            c.showPage()
                            y = height - inch
                        c.drawString(inch, y, line[:80])
                        y -= 0.2 * inch
                        
                        # Update progress
                        progress = 30 + (i / total_lines) * 60
                        self.update_progress(progress, f"Converting text... {int(progress)}%")
                    
                    c.save()
                    self.update_progress(100, "✅ Text converted to PDF!")
                    self.show_success_popup(f'✅ Text file converted and saved in: {os.path.basename(dest_folder)}')
                    return
                except ImportError:
                    # Copy with progress
                    self.update_progress(30, "Copying file...")
                    with open(source_file, 'rb') as src, open(pdf_path, 'wb') as dst:
                        while True:
                            chunk = src.read(chunk_size)
                            if not chunk:
                                break
                            dst.write(chunk)
                            copied_size += len(chunk)
                            progress = min(90, 30 + (copied_size / file_size) * 60)
                            self.update_progress(progress, "Copying file...")
                    
                    self.update_progress(100, "⚠️ File copied (conversion unavailable)")
                    self.show_success_popup(f'⚠️ Text file copied (conversion unavailable)')
                    return
            
            # Any other file - copy with progress
            self.update_progress(30, "Copying file...")
            with open(source_file, 'rb') as src, open(pdf_path, 'wb') as dst:
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
                    copied_size += len(chunk)
                    progress = min(90, 30 + (copied_size / file_size) * 60)
                    self.update_progress(progress, "Copying file...")
            
            self.update_progress(100, "✅ File saved!")
            self.show_success_popup(f'✅ File saved in: {os.path.basename(dest_folder)}')
            
        except Exception as e:
            self.update_progress(0, "❌ Error")
            self.show_error_popup(f'Error: {str(e)}')
    
    def show_success_popup(self, message):
        popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        popup_content.add_widget(Label(
            text=message,
            font_size=16,
            color=(0.1, 0.5, 0.1, 1)
        ))
        
        btn_layout = BoxLayout(spacing=10, size_hint=(1, 0.3))
        close_btn = Button(text='OK', size_hint=(0.5, 1))
        view_btn = Button(text='📄 View Files', size_hint=(0.5, 1))
        popup_content.add_widget(btn_layout)
        btn_layout.add_widget(close_btn)
        btn_layout.add_widget(view_btn)
        
        popup = Popup(
            title='Success',
            content=popup_content,
            size_hint=(0.8, 0.5)
        )
        
        def on_close(btn):
            popup.dismiss()
            self.progress_bar.value = 0
            self.progress_label.text = 'Progress: 0%'
        
        def on_view(btn):
            popup.dismiss()
            view_screen = self.manager.get_screen('view_files')
            view_screen.current_path = self.current_folder
            view_screen.show_only_folders = False
            view_screen.refresh_files(None)
            self.manager.current = 'view_files'
            self.progress_bar.value = 0
            self.progress_label.text = 'Progress: 0%'
        
        close_btn.bind(on_press=on_close)
        view_btn.bind(on_press=on_view)
        popup.open()
    
    def show_error_popup(self, message):
        popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        popup_content.add_widget(Label(
            text=message,
            font_size=16,
            color=(0.8, 0.2, 0.2, 1)
        ))
        close_btn = Button(text='OK', size_hint=(1, 0.3))
        popup_content.add_widget(close_btn)
        
        popup = Popup(
            title='Error',
            content=popup_content,
            size_hint=(0.8, 0.4)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        self.progress_bar.value = 0
        self.progress_label.text = 'Progress: 0%'
        self.manager.current = 'create_folder'


# ============================================
# Screen 4: View Files Screen
# ============================================
class ViewFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_path = None
        self.show_only_folders = True  # Start with only folders
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint=(1, 0.08), spacing=10)
        header.add_widget(Label(
            text='📄 My Files',
            font_size=28,
            bold=True,
            color=(0.05, 0.15, 0.4, 1)
        ))
        layout.add_widget(header)
        
        # Current path
        self.path_label = Label(
            text='📁 Path: Not selected',
            font_size=16,
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.05)
        )
        layout.add_widget(self.path_label)
        
        # File list
        self.file_list = ScrollView(size_hint=(1, 0.77))
        self.file_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.file_list_layout.bind(minimum_height=self.file_list_layout.setter('height'))
        self.file_list.add_widget(self.file_list_layout)
        layout.add_widget(self.file_list)
        
        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.08), spacing=10)
        
        refresh_btn = Button(
            text='🔄 Refresh',
            background_color=(0.15, 0.4, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        refresh_btn.bind(on_press=self.refresh_files)
        btn_layout.add_widget(refresh_btn)
        
        back_btn = Button(
            text='🔙 Back',
            background_color=(0.4, 0.4, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(back_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def on_enter(self):
        if not self.current_path:
            home_screen = self.manager.get_screen('home')
            if home_screen.base_folder:
                self.current_path = home_screen.base_folder
        self.show_only_folders = True  # Always show folders first when entering
        self.refresh_files(None)
    
    def refresh_files(self, instance):
        """Refresh the file list - shows folders first, then files only when navigated"""
        self.file_list_layout.clear_widgets()
        
        if not self.current_path or not os.path.exists(self.current_path):
            self.path_label.text = '📁 Path: Not selected'
            no_files = Label(
                text='Please select a folder first',
                font_size=18,
                color=(0.5, 0.5, 0.5, 1)
            )
            self.file_list_layout.add_widget(no_files)
            return
        
        self.path_label.text = f'📁 Path: {self.current_path}'
        
        try:
            items = os.listdir(self.current_path)
            
            if not items:
                no_files = Label(
                    text='📭 No folders or files in this location',
                    font_size=18,
                    color=(0.5, 0.5, 0.5, 1)
                )
                self.file_list_layout.add_widget(no_files)
                return
            
            # Separate folders and files
            folders = []
            files = []
            
            for item in items:
                item_path = os.path.join(self.current_path, item)
                if os.path.isdir(item_path):
                    folders.append(item)
                else:
                    files.append(item)
            
            # Show folders
            if folders:
                header = BoxLayout(size_hint_y=None, height=40)
                header.add_widget(Label(
                    text='📁 Folders',
                    font_size=20,
                    bold=True,
                    color=(0.05, 0.15, 0.4, 1)
                ))
                self.file_list_layout.add_widget(header)
                
                for folder in sorted(folders):
                    folder_row = BoxLayout(size_hint_y=None, height=45, spacing=5)
                    
                    folder_label = Label(
                        text=f'📁 {folder}',
                        font_size=18,
                        color=(0.1, 0.1, 0.1, 1),
                        size_hint=(0.8, 1)
                    )
                    folder_row.add_widget(folder_label)
                    
                    # Open folder button - navigates into folder
                    open_btn = Button(
                        text='📂 Open',
                        size_hint=(0.2, 0.8),
                        background_color=(0.15, 0.4, 0.7, 1),
                        color=(1, 1, 1, 1),
                        font_size=14
                    )
                    open_btn.bind(on_press=lambda x, f=folder: self.open_folder(f))
                    folder_row.add_widget(open_btn)
                    
                    self.file_list_layout.add_widget(folder_row)
            
            # Show files ONLY if show_only_folders is False
            if not self.show_only_folders and files:
                header = BoxLayout(size_hint_y=None, height=40)
                header.add_widget(Label(
                    text='📄 Files',
                    font_size=20,
                    bold=True,
                    color=(0.05, 0.15, 0.4, 1)
                ))
                self.file_list_layout.add_widget(header)
                
                for file in sorted(files):
                    file_row = BoxLayout(size_hint_y=None, height=45, spacing=5)
                    
                    file_label = Label(
                        text=f'📄 {file}',
                        font_size=16,
                        color=(0.1, 0.1, 0.1, 1),
                        size_hint=(0.8, 1)
                    )
                    file_row.add_widget(file_label)
                    
                    # Open file button
                    open_btn = Button(
                        text='📖 Open',
                        size_hint=(0.2, 0.8),
                        background_color=(0.15, 0.4, 0.7, 1),
                        color=(1, 1, 1, 1),
                        font_size=14
                    )
                    open_btn.bind(on_press=lambda x, f=file: self.open_file(f))
                    file_row.add_widget(open_btn)
                    
                    self.file_list_layout.add_widget(file_row)
            
            # If only showing folders and there are no folders
            if self.show_only_folders and not folders:
                no_folders = Label(
                    text='📭 No folders created yet.\nClick "Create Folder" to add one.',
                    font_size=18,
                    color=(0.5, 0.5, 0.5, 1)
                )
                self.file_list_layout.add_widget(no_folders)
            
            # If showing files and there are no files
            if not self.show_only_folders and folders and not files:
                no_files = Label(
                    text='📭 No files in this folder.\nClick "Upload" to add files.',
                    font_size=18,
                    color=(0.5, 0.5, 0.5, 1)
                )
                self.file_list_layout.add_widget(no_files)
                    
        except Exception as e:
            error_label = Label(
                text=f'❌ Error: {str(e)}',
                font_size=16,
                color=(0.8, 0.2, 0.2, 1)
            )
            self.file_list_layout.add_widget(error_label)
    
    def open_folder(self, folder_name):
        """Navigate into a folder - shows files inside"""
        home_screen = self.manager.get_screen('home')
        new_path = os.path.join(self.current_path, folder_name)
        home_screen.current_folder = new_path
        self.current_path = new_path
        self.show_only_folders = False  # Show files inside the folder
        self.refresh_files(None)
        
        # Update upload screen folder
        upload_screen = self.manager.get_screen('upload')
        upload_screen.current_folder = new_path
    
    def open_file(self, filename):
        """Open a file with default application"""
        file_path = os.path.join(self.current_path, filename)
        
        try:
            os.startfile(file_path)
            popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
            popup_content.add_widget(Label(
                text=f'✅ Opening file:\n\n{filename}',
                font_size=16,
                color=(0.1, 0.1, 0.1, 1)
            ))
            close_btn = Button(text='OK', size_hint=(1, 0.3))
            popup_content.add_widget(close_btn)
            
            popup = Popup(
                title='Opening File',
                content=popup_content,
                size_hint=(0.8, 0.4)
            )
            close_btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            popup_content = BoxLayout(orientation='vertical', padding=20, spacing=10)
            popup_content.add_widget(Label(
                text=f'❌ Error opening file:\n\n{str(e)}',
                font_size=16,
                color=(0.8, 0.2, 0.2, 1)
            ))
            close_btn = Button(text='OK', size_hint=(1, 0.3))
            popup_content.add_widget(close_btn)
            
            popup = Popup(
                title='Error',
                content=popup_content,
                size_hint=(0.8, 0.4)
            )
            close_btn.bind(on_press=popup.dismiss)
            popup.open()
    
    def go_back(self, instance):
        # Reset to show only folders when going back to home
        self.show_only_folders = True
        self.manager.current = 'home'


# ============================================
# Main Application
# ============================================
class PaperVaultApp(App):
    def build(self):
        self.title = 'PaperVault - Test Paper Manager'
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CreateFolderScreen(name='create_folder'))
        sm.add_widget(UploadScreen(name='upload'))
        sm.add_widget(ViewFilesScreen(name='view_files'))
        
        return sm

if __name__ == '__main__':
    PaperVaultApp().run()