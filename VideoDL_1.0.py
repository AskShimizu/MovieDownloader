from yt_dlp import YoutubeDL
import tkinter as tk
from tkinter import Menu, messagebox as msg, font, filedialog, ttk
import os
from time import sleep
from threading import Thread

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master.geometry("800x500")
        self.master.title("Video Downloader X")
        self.master.resizable(False, False) # ユーザによる窓サイズ変更禁止
        # self.iconfile = "./favicon.ico"
        # self.master.iconbitmap(default=self.iconfile)
        self.create_widgets()

    def create_widgets(self):
        self.font01 = font.Font(family="Helvetica", size=15, weight="normal")
        self.font02 = font.Font(family='Helvetica', size=15, weight='bold')
        self.font03 = font.Font(family='Helvetica', size=30, weight='bold')
        
        self.menu_bar = Menu(self.master)
        self.master.config(menu=self.menu_bar)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label='Exit', command=self._quit)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label='About', command=self._msgBox)
        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)

        self.lbl_main = ttk.Label(self.master, text='Video Downloader', font=self.font03)
        self.lbl_main.place(relx=0.25, rely=0.1) #タイトル座標

        self.frame_form = tk.Label(self.master)
        self.frame_form.place(relx=0.01, rely=0.25, height=400, width=780)
        
        self.lbl_URL = ttk.Label(self.frame_form, text='URL', font=self.font01)
        self.lbl_URL.grid(column=0, row=0, padx=20, pady=20)
        self.URL_name = tk.StringVar()
        self.ent_URL = ttk.Entry(self.frame_form, textvariable=self.URL_name, width=35, font=self.font01)
        self.ent_URL.grid(column=1, row=0, padx=20, pady=20)
        self.ent_URL.focus()

        # Pasteボタン
        self.btn_Paste = tk.Button(self.frame_form, text='Paste', font=self.font02, command=self.paste_text)
        self.btn_Paste.grid(column=2, row=0, padx=0, pady=0)
        # Deleteボタン
        self.btn_Delete = tk.Button(self.frame_form, text='Del', font=self.font02, command=self.clear_text)
        self.btn_Delete.grid(column=3, row=0, padx=0, pady=0)

        self.Folder_name = tk.StringVar()
        self.lbl_folder = ttk.Label(self.frame_form, text='DL Folder', font=self.font01)
        self.lbl_folder.grid(column=0, row=1, padx=20, pady=20)
        self.ent_Folder = ttk.Entry(self.frame_form, textvariable=self.Folder_name, width=35, font=self.font01)
        self.ent_Folder.grid(column=1, row=1, padx=20, pady=20)
        self.btn_Folder = tk.Button(self.frame_form, text='Select', font=self.font02, command=self._get_Folder_Path)
        self.btn_Folder.grid(column=2, row=1, padx=20, pady=20, sticky=tk.W + tk.E)

        # ファイル名指定エントリ
        self.lbl_filename = ttk.Label(self.frame_form, text='File Name', font=self.font01)
        self.lbl_filename.grid(column=0, row=2, padx=20, pady=20)
        self.File_name = tk.StringVar()
        self.ent_File_name = ttk.Entry(self.frame_form, textvariable=self.File_name, width=35, font=self.font01)
        self.ent_File_name.grid(column=1, row=2, padx=20, pady=20)

        self.btn_Start = tk.Button(self.frame_form, text='DL Start', font=self.font02, command=self.click_me)
        self.btn_Start.grid(column=1, row=3, padx=20, pady=20, sticky=tk.W + tk.E)

        self.progress_bar = ttk.Progressbar(self.frame_form, orient='horizontal', length=286, mode='determinate')
        self.progress_bar.grid(column=1, row=4, padx=20, pady=12, sticky=tk.W + tk.E)

    def paste_text(self):
        """クリップボードの最新テキストをURLエントリにペーストする"""
        clipboard_text = self.master.clipboard_get()
        self.URL_name.set(clipboard_text)

    def clear_text(self):
        """URLエントリの内容をすべて削除する"""
        self.URL_name.set("")
    
    def click_me(self):
        url = self.URL_name.get()
        folder = self.Folder_name.get()
        
        if not url:
            msg.showerror("Error", "Please enter a video URL.")
            return
        if not folder:
            msg.showerror("Error", "Please select a download folder.")
            return

        self.create_thread()

    def create_thread(self):
        self.run_thread = Thread(target=self.method_in_a_thread)
        self.run_thread.start()

    def method_in_a_thread(self):
        self.download_video(self.URL_name.get(), self.Folder_name.get())

    def _msgBox(self):
        msg.showinfo('Program Information', 'Video Downloader with Tkinter \n (c) 2020 Tomomi Research Inc.')

    def download_video(self, url, download_folder):
        file_name = self.File_name.get()
        if not file_name:
            file_name = "%(title)s"  # デフォルトのファイル名

        # 保存するファイルパスを生成
        output_path = os.path.join(download_folder, f'{file_name}.%(ext)s')

        # 同名ファイルの存在チェック
        if any(os.path.exists(output_path.replace('%(ext)s', ext)) for ext in ['mp4', 'mkv', 'webm']):
            msg.showerror("Error", "A file with the same name already exists. Please choose a different file name.")
            return  # ダウンロード中断

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_path,  # ファイル名のテンプレート
            'progress_hooks': [self.progress_hook],  # プログレスバーのフック
            'no_color': True  # 色付きのテキストを無効化
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            msg.showinfo("Success", "Download completed.")
        except Exception as e:
            msg.showerror("Error", f"Failed to download video. {e}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').strip('%')
            self.progress_bar["value"] = float(p)
            self.progress_bar.update()
        elif d['status'] == 'finished':
            self.progress_bar["value"] = 100
            self.progress_bar.update()

    def _quit(self):
        self.master.quit()
        self.master.destroy()
        exit()

    def _get_Folder_Path(self):
        folder_path = filedialog.askdirectory(initialdir=os.path.abspath(os.path.dirname(__file__)))
        self.Folder_name.set(folder_path)

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
