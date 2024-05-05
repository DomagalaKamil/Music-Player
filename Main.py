from pathlib import Path
import pygame
import random
from pygame import mixer
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Scale, HORIZONTAL, ttk, Menu, Toplevel, Label, Checkbutton, BooleanVar, Scrollbar, Frame
import subprocess
import sys
import os
import re
import random
import time 

# Initialize pygame mixer
pygame.init()
pygame.mixer.init()

####################################

            #Variables

####################################

random_mode = False
played_songs = []
recently_played_songs = []
queue_songs = []
is_playing = False  
current_song_index = 0 
is_paused = False
is_muted = False
previous_volume = 50


####################################

 #Set path to folder, create folders

####################################
desktop_path = Path.home() / 'Desktop'
MUSIC_PATH = desktop_path / 'Music'
repeat_playlist = False 

def open_folder(path):
    if sys.platform == "win32": # windows
        os.startfile(path)
    elif sys.platform == "darwin":  # macOS
        subprocess.Popen(["open", path])
    else:  # linux
        subprocess.Popen(["xdg-open", path])

def create_and_open_music_folder():
    desktop_path = Path.home() / 'Desktop'
    music_folder = desktop_path / 'Music'
    if not music_folder.exists():
        music_folder.mkdir()  # Create folder if it does not exist
    open_folder(music_folder)  # Open folder

def ensure_directory_exists(path):
    if not path.exists():
        path.mkdir(parents=True) 

def create_playlist_folder():
    # First, ensure the Music folder exists
    ensure_directory_exists(MUSIC_PATH)
    
    # Now, handle the Playlists folder
    playlist_folder = MUSIC_PATH / 'Playlists'
    ensure_directory_exists(playlist_folder)
    return playlist_folder

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

pygame.mixer.init()

####################################

  #Create playlist window creation

####################################
def refresh_playlist_list(treeview):
    load_playlists(treeview)

def open_playlist_creation_window():
    playlist_folder = create_playlist_folder()  # Ensure the playlist folder exists

    # Create a new window for playlist creation
    playlist_window = Toplevel(window)
    playlist_window.title("Create Playlist")
    playlist_window.geometry("500x700")  # Increased height to accommodate scrollbar

    # Frame for Entry and Label
    entry_frame = Frame(playlist_window)
    entry_frame.pack(fill='x', padx=10, pady=10)

    # Label for input
    Label(entry_frame, text="Enter Playlist Name:").pack(side='left')

    # Entry widget for playlist name
    playlist_name_entry = Entry(entry_frame, width=20)
    playlist_name_entry.pack(side='left')

    # Canvas and scrollbar for songs
    canvas = Canvas(playlist_window)
    scrollbar = Scrollbar(playlist_window, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)

    # Configuring the canvas to accept the scrollable frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # List music files and checkboxes
    song_var_dict = {}
    music_files = list(MUSIC_PATH.glob('*.mp3')) 
    for song in music_files:
        var = BooleanVar()
        checkbox = Checkbutton(scrollable_frame, text=song.stem, variable=var)
        checkbox.pack(anchor='w')
        song_var_dict[song.stem] = var

    # Pack canvas and scrollbar in the window
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    def save_playlist():
        playlist_name = playlist_name_entry.get().strip()
        if playlist_name:  # Check if playlist name is not empty
            playlist_path = playlist_folder / f"{playlist_name}.txt"
            with open(playlist_path, 'w') as file:
                for song in music_files:
                    if song_var_dict[song.stem].get():
                        file.write(f"{song.name}\n")  # Save the song name
            playlist_window.destroy()
            refresh_playlist_list(playlist_list)
    # Button to save the playlist
    save_button = Button(playlist_window, text="Save Playlist", command=save_playlist)
    save_button.pack(pady=(10, 0))

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\Domag\Desktop\build\assets\frame0")

####################################

            #Load Files

####################################

def get_music_files():
    global all_songs
    music_files = []
    extensions = ["*.mp3", "*.wav", "*.aac", "*.flac"]
    for extension in extensions:
        music_files.extend(MUSIC_PATH.glob(extension))
    all_songs = music_files.copy()  
    return music_files 

def load_songs():
    global all_songs, current_song_index
    all_songs = get_music_files()
    library_list.delete(*library_list.get_children())  # Clear the existing entries in the Treeview
    for song_path in all_songs:
        song_name = song_path.stem
        library_list.insert("", "end", text=song_name, values=(song_name,))
    current_song_index = -1  # Reset index to start from the beginning or any specific song as needed


def load_playlists(treeview):
    # Clear existing items in the treeview
    for item in treeview.get_children():
        treeview.delete(item)

    # playlists are stored as .txt files in the 'Playlists' folder
    playlists = list((MUSIC_PATH / 'Playlists').glob('*.txt'))
    for playlist in playlists:
        playlist_name = playlist.stem
        # Insert each playlist into the treeview
        treeview.insert('', 'end', text=playlist_name, values=(playlist_name,))

    # Bind the selection event
    treeview.bind("<<TreeviewSelect>>", load_playlist_content)

def load_playlist_content(event):
    global current_playlist_songs, in_playlist_mode

    item_id = event.widget.selection()[0]
    playlist_name = event.widget.item(item_id, 'text')
    playlist_file_path = MUSIC_PATH / 'Playlists' / f'{playlist_name}.txt'

    if not playlist_file_path.exists():
        print(f"No playlist file found for {playlist_name}")
        return

    current_playlist_songs = []  # Clear previous playlist songs
    with open(playlist_file_path, 'r') as file:
        for line in file:
            song_file = line.strip()
            full_song_path = MUSIC_PATH / song_file  
            if full_song_path.exists():
                current_playlist_songs.append(str(full_song_path)) 
            else:
                print(f"Song file {song_file} not found in directory.")
    
    in_playlist_mode = True
    library_list.delete(*library_list.get_children())
    for song_path in current_playlist_songs:
        song_name = Path(song_path).stem
        library_list.insert("", "end", text=song_name, values=(song_name,))

    print("Playlist loaded. Please select a song to play.")


####################################

           #Display Files

####################################


def display_playlists(canvas, scrollable_frame):
    # Clear previous items
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    playlists = load_playlists()
    for playlist in playlists:
        playlist_name = playlist.stem
        button = Button(scrollable_frame, text=playlist_name, command=lambda p=playlist: print(f"Selected playlist: {p}"),
                        width=200, height=50, bg="#252525", fg="#FFFFFF", relief='flat')
        button.pack(pady=10, padx=10, fill='x')  

####################################

           #Create Canvas

####################################

def create_playlist_area(window):
    global playlist_list
    playlist_frame = tk.Frame(window, bg="#252525", bd=0, highlightthickness=0)
    playlist_frame.place(x=1269, y=50, width=315, height=350)

    playlist_label = tk.Label(playlist_frame, text="Playlists", bg="#252525", fg="#FFFFFF", font=('Helvetica', 16))
    playlist_label.pack()


    # Styling for Treeview
    style = ttk.Style()
    style.theme_use("default") 
    style.configure("Treeview",
                    background="#252525",
                    fieldbackground="#252525",
                    foreground="#FFFFFF",
                    font=('Helvetica', 12),
                    borderwidth=0)
    style.map('Treeview',
              background=[('selected', '#005500')])

    # Treeview widget for showing playlists
    playlist_list = ttk.Treeview(playlist_frame, show="tree", selectmode="browse")
    playlist_list.pack(fill=tk.BOTH, expand=True)

    # Load playlists into the Treeview
    load_playlists(playlist_list)

    return playlist_frame

def create_queue_area(window):
    # Frame for queued songs
    queue_frame = tk.Frame(window, bg="#252525", bd=0, highlightthickness=0)  
    queue_frame.place(x=1269, y=440, width=315, height=300)  

    queue_label = tk.Label(queue_frame, text="Queued Songs", bg="#252525", fg="#FFFFFF", font=('Helvetica', 16))
    queue_label.pack()

    # Text box for displaying queued songs
    queue_text = tk.Text(queue_frame, bg="#252525", fg="#FFFFFF", font=('Helvetica', 12), relief='flat', borderwidth=0)
    queue_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)  

    
    clear_queue_button = tk.Button(queue_frame, text="Clear Queue", command=lambda: clear_queue(queue_text))
    clear_queue_button.pack()

    return queue_frame, queue_text


####################################

           #Queue Managment

####################################

def add_to_queue(event):
    # Check if any item is selected in the library_list
    if not library_list.selection():
        print("No item selected in the library.")
        return  
    
    selected_item = library_list.selection()[0]
    song_name = library_list.item(selected_item, 'text')

    # Add the selected song to the queue
    queue_songs.append(song_name)

    # Update the queue display
    update_queue_list(queue_text)


def update_queue_list(queue_text):
    queue_text.delete(1.0, tk.END)  # Clear the current text
    for song in queue_songs:
        queue_text.insert(tk.END, f"{song}\n") 


def clear_queue():
    global queue_songs
    queue_songs = []
    update_queue_list(queue_text)

def add_to_queue_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

####################################

       #Random/Repeat Function

####################################


def toggle_random_mode():
    global random_mode, is_playing
    random_mode = not random_mode  # Toggle random mode
    update_button_image()  

    # Stop current music if playing
    if is_playing:
        pygame.mixer.music.stop()
        is_playing = False
        canvas.itemconfig(song_title_text, text="Playing:")  # Clear the song title

    if random_mode:
        # If random mode just turned on, play a random song immediately
        play_song()

def toggle_repeat():
    global repeat_playlist
    repeat_playlist = not repeat_playlist
    repeat.config(image=repeat_true_image if repeat_playlist else repeat_false_image)

    if repeat_playlist and current_song_index == len(current_playlist_songs) - 1:
        # If currently on the last song and repeat is turned on, restart the playlist
        play_song(0)
    elif not repeat_playlist and current_song_index == len(current_playlist_songs) - 1:
        # If the repeat is turned off and on the last song, stop or switch mode
        on_switch_to_library() 


####################################

        #Play Functions

####################################

def play_song_decoder(event):
    # Get the selected item in the library list
    selected_item = library_list.selection()[0]
    song_name = library_list.item(selected_item, 'text')
    
    # Find the index of the song in the all_songs list
    try:
        index = next(i for i, song in enumerate(all_songs) if song.stem == song_name)
        play_song(index)  # Call the play_song function with the index
        # Remove the song from the queue if it's in there
        if song_name in queue_songs:
            queue_songs.remove(song_name)
            update_queue_list(queue_text)
    except StopIteration:
        print("Selected song is not found in the song list.")


def on_song_selected(event):
    selected_index = library_list.index(library_list.selection()[0])  # Get index of selected item
    play_song(index=selected_index)


def play_song(index=None):
    global current_song_index, is_playing, current_playlist_songs, in_playlist_mode, repeat_playlist, recently_played_songs, played_songs, queue_songs, song_title

    if in_playlist_mode:
        song_list = current_playlist_songs
    else:
        song_list = all_songs
    
    if random_mode:
        available_songs = [song for song in song_list if song not in played_songs]
        if not available_songs:  # If all songs have been played
            played_songs = []  # Reset the played songs list
            available_songs = song_list.copy()  # Reset available songs to all songs
        index = random.choice([song_list.index(song) for song in available_songs])
    else:
        if index is None:
            index = (current_song_index + 1) % len(song_list)
        elif index >= len(song_list):
            if in_playlist_mode and repeat_playlist:
                index = 0  # Restart the playlist
            else:
                if in_playlist_mode:
                    on_switch_to_library()  # If not repeating, switch to library
                return

    current_song_index = index
    song_path = song_list[index]

    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()

    song_title = Path(song_path).stem
    canvas.itemconfig(song_title_text, text=f"Playing: {song_title}")
    is_playing = True

    # Remove the currently playing song from the queue
    if song_title in queue_songs:
        queue_songs.pop(0)  # Remove the first song in the queue
        update_queue_list(queue_text)

    # Manage recently played songs
    if song_title not in recently_played_songs or recently_played_songs[0] != song_title:
        recently_played_songs.insert(0, song_title)  # Add to the start of the list
        if len(recently_played_songs) > 25:
            recently_played_songs.pop()  

    update_recently_played_songs()  
    
    # Start updating the progress bar
    update_progress_bar(song_path)

# Function to update the progress bar during playback
def update_progress_bar(song_path):
    total_length = get_total_length(song_path)
    while pygame.mixer.music.get_busy():
        current_time = get_current_time()
        progress = (current_time / total_length) * 100
        progress_bar['value'] = progress
        window.update()  # Update the tkinter window to refresh the progress bar


def check_music_end():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:  # Song has ended
            play_song()  # Play the next song according to the current settings





current_playlist_songs = []  # List to store the current playlist's songs
in_playlist_mode = False  # Flag to determine if the player is in playlist mode
repeat_playlist = False  # New variable to manage repeat state


####################################

        #Progress Bar Functions

####################################

def get_current_time():
    if pygame.mixer.music.get_busy():
        return pygame.mixer.music.get_pos() // 1000  # Convert milliseconds to seconds
    else:
        return 0

# Function to get the total length of the music
def get_total_length(song_path):
    sound = pygame.mixer.Sound(song_path)
    return sound.get_length()

####################################

      #Library Switch Functions

####################################

def on_switch_to_library():
    global in_playlist_mode, current_song_index
    in_playlist_mode = False
    current_song_index = -1  # Reset the index
    load_songs()

def on_switch_to_playlist():
    global in_playlist_mode, current_song_index
    current_song_index = -1  # Reset the index
    in_playlist_mode = True
    
    load_playlist(selected_playlist_name)


pygame.mixer.music.set_endevent(pygame.USEREVENT) 


####################################

      #Updating canvas functions

####################################

def update_recently_played_songs():
    canvas.delete("recently_played")  # Clear previous entries
    
    x_start = 30
    y_start = 236
    max_width = 300 
    line_height = 40  

    clip_rect = canvas.create_rectangle(
        x_start, y_start, x_start + max_width, 750,
        outline="", fill=""  
    )

    # Use a loop to display each song in the recently played list
    for index, song in enumerate(recently_played_songs):
        text_id = canvas.create_text(
            x_start, y_start + index * line_height,  # Increment y for each new text item
            anchor="nw",
            text=song,
            width=max_width,  # Limits the text to a certain width
            fill="#FFFFFF",
            font=("Inter", 16 * -1),
            tag="recently_played"
        )
        # Ensure text does not overflow vertically
        if y_start + (index + 1) * line_height > 750:  
            break


# Initialize music files at the start
music_files = get_music_files()

def update_button_image():
    if random_mode:
        shuffle.config(image=shuffle_image_true)  
    else:
        shuffle.config(image=shuffle_image_false)


####################################

          #Control Functions

####################################


# Pause the currently playing song
def pause_song():
    global is_paused
    mixer.music.pause()
    is_paused = True

# Resume the paused song
def resume_song():
    global is_paused
    mixer.music.unpause()
    is_paused = False

def toggle_play_pause():
    global is_paused
    if is_paused:
        resume_song()
    else:
        pause_song()

def skip_next():
    global current_song_index

    # Check if there are songs in the queue
    if queue_songs:
        # Remove the first song from the queue
        song_name = queue_songs.pop(0)
        update_queue_list(queue_text)
        try:
            # Find the index of the song in the all_songs list
            index = next(i for i, song in enumerate(all_songs) if song.stem == song_name)
            play_song(index)  # Play the song
            # Remove the displayed song from the queue text box
            update_queue_list(queue_text)
        except StopIteration:
            print("Selected song is not found in the song list.")
    else:
        # If there are no songs in the queue, proceed to the next song in the current list
        current_song_index += 1
        if current_song_index < len(all_songs):
            play_song(current_song_index)
        else:
            # If it's the last song, stop or switch mode
            on_switch_to_library()  


def skip_previous():
    global current_song_index
    if current_song_index > 0:
        play_song(current_song_index - 1)

def toggle_mute():
    global is_muted, previous_volume
    current_volume = volume_slider.get()
    if not is_muted:
        previous_volume = current_volume  # Save current volume
        pygame.mixer.music.set_volume(0)  # Mute the sound
        mute.config(image=mute_true_image)  # Change button image to muted
        is_muted = True
    else:
        pygame.mixer.music.set_volume(previous_volume / 100)  # Restore the sound
        volume_slider.set(previous_volume)  # Update slider position
        mute.config(image=mute_false_image)  # Change button image to unmuted
        is_muted = False


# Setup the volume slider
def adjust_volume(value):
    if not is_muted:
        volume_level = float(value) / 100  # Convert to 0.0 - 1.0 scale
        pygame.mixer.music.set_volume(volume_level)
####################################

          #Create Cavnas
          #Load Objects

####################################


window = tk.Tk()
window.geometry("1660x900")
window.configure(bg = "#1B1B1B")
context_menu = Menu(window, tearoff=0)
context_menu.add_command(label="Add to Queue", command=add_to_queue)
canvas = Canvas(
    window,
    bg = "#1B1B1B",
    height = 900,
    width = 1600,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Layout the canvas and scrollbar in the window
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

canvas.place(x = 0, y = 0)
# Define the image for the 'add_music' button
add_music_image = PhotoImage(
    file=relative_to_assets("add_music.png"))  

# Create the 'add_music' button
add_music = Button(
    image=add_music_image,
    borderwidth=0,
    highlightthickness=0,
    command=create_and_open_music_folder,  
    relief="flat"
)
add_music.place(
    x=25.0,  
    y=30.0,  
    width=298.0,  
    height=50.0  
)

canvas.create_rectangle(
        20, 190, 350, 750,  
        fill="#252525", outline="",
        tag="recently_played_background"
    )

canvas.create_text(
    28.0,
    194.0,
    anchor="nw",
    text="Recently Played",
    fill="#FFFFFF",
    font=("Inter", 25 * -1)
)

create_playlist_area(window)
queue_frame, queue_text = create_queue_area(window)

# Create a button that looks like the text label and specify width and height
library_button = Button(window, text="Library", command=load_songs,
                        bg="#1B1B1B", fg="#FFFFFF", font=("Inter", 18),
                        borderwidth=0, highlightthickness=0, relief="flat")
library_button.place(x=400, y=15, width=100, height=38) 


# Define the image for the 'create_playlist' button
create_playlist_image = PhotoImage(
    file=relative_to_assets("create_playlist.png")) 

# Create the 'create_playlist' button
create_playlist = Button(
    image=create_playlist_image,
    borderwidth=0,
    highlightthickness=0,
    command=open_playlist_creation_window,  
    relief="flat"
)
create_playlist.place(
    x=25.0,  
    y=104.0,  
    width=298.0,  
    height=50.0 
)


music_list_frame = tk.Frame(window)
music_list_frame.place(x=400, y=50, width=800, height=690)

style = ttk.Style()
style.theme_use("default")  # Start with the default theme to modify it
style.configure("Treeview", background="#252525", fieldbackground="#252525", foreground="#FFFFFF", font=('Helvetica', 12), borderwidth=0)
style.map('Treeview', background=[('selected', '#005500')])


# Treeview widget for showing songs
library_list = ttk.Treeview(music_list_frame, columns=("name"), show="tree", selectmode="browse", padding=[-745, 0, 0, 0])
library_list.pack(fill=tk.BOTH, expand=True)
library_list.bind("<Double-1>", on_song_selected) 
library_list.bind("<Button-3>", lambda event: add_to_queue(event))
load_songs() 



# Define the image for the 'play_pause' button
play_pause_image = PhotoImage(
    file=relative_to_assets("play_pause.png")) 

# Create the 'play_pause' button
play_pause = Button(
    image=play_pause_image,
    borderwidth=0,
    highlightthickness=0,
    command=toggle_play_pause,  
    relief="flat"
)
play_pause.place(
    x=775.0, 
    y=784.0,  
    width=50.0, 
    height=50.0  
)


shuffle_image_false = PhotoImage(file=relative_to_assets("shuffle_false.png"))
shuffle_image_true = PhotoImage(file=relative_to_assets("shuffle_true.png"))

# Create the 'shuffle' button initially with 'shuffle_false' image
shuffle = Button(
    image=shuffle_image_false,
    borderwidth=0,
    highlightthickness=0,
    command=toggle_random_mode,
    relief="flat"
)
shuffle.place(
    x=651.0,  
    y=784.0,  
    width=50.0, 
    height=50.0 
)


repeat_false_image = PhotoImage(file=relative_to_assets("repeat_false.png"))
repeat_true_image = PhotoImage(file=relative_to_assets("repeat_true.png"))
# Create the 'repeat' button initially with 'repeat_false' image

repeat = Button(
    image=repeat_false_image,
    borderwidth=0,
    highlightthickness=0,
    command=toggle_repeat,  
    relief="flat"
)
repeat.place(
    x=899.0,  
    y=784.0,  
    width=50.0, 
    height=50.0  
)

# Define the image for the 'skip_backwards' button
skip_backward_image = PhotoImage(
    file=relative_to_assets("skip_backward.png"))  

# Create the 'skip_backwards' button
skip_backwards = Button(
    image=skip_backward_image,
    borderwidth=0,
    highlightthickness=0,
    command=skip_previous,  
    relief="flat"
)
skip_backwards.place(
    x=713.0,  
    y=784.0,  
    width=50.0,  
    height=50.0  
)


# Define the image for the 'skip_forwards' button
skip_forward_image = PhotoImage(
    file=relative_to_assets("skip_forward.png")) 

# Create the 'skip_forwards' button
skip_forwards = Button(
    image=skip_forward_image,
    borderwidth=0,
    highlightthickness=0,
    command=skip_next,  
    relief="flat"
)
skip_forwards.place(
    x=837.0, 
    y=784.0,  
    width=50.0,  
    height=50.0  
)

volume_slider = ttk.Scale(
    window,
    from_=0,  # Minimum volume level (0%)
    to=100,  # Maximum volume level (100%)
    orient="horizontal",
    command=adjust_volume  
)
volume_slider.place(x=1330.0, y=810.0, width=242.0, height=22.0)
volume_slider.set(50)  # Set the slider initially to 50%

mute_false_image = PhotoImage(file=relative_to_assets("mute_false.png")) 
mute_true_image = PhotoImage(file=relative_to_assets("mute_true.png"))  

# Create the 'mute' button initially with 'mute_false' image
mute = Button(
    image=mute_false_image,
    borderwidth=0,
    highlightthickness=0,
    command=toggle_mute,  
    relief="flat"
)
mute.place(
    x=1268.0,  
    y=796.0,  
    width=50.0,  
    height=50.0  
)

# Configure a custom style for the slider to appear green
style = ttk.Style()
style.theme_use('default')
style.configure("Horizontal.TScale", troughcolor="#1B1B1B", background="green")


song_title_text = canvas.create_text(
    80.0,
    800.0,  
    anchor="nw",
    text="",
    fill="#FFFFFF",
    font=("Inter", 16 * -1)
)

progress_bar = ttk.Progressbar(window, orient="horizontal", mode="determinate", length=700)
progress_bar.place(x=450.0, y=846.0)


button_image_11 = PhotoImage(
    file=relative_to_assets("button_11.png"))
button_11 = Button(
    image=button_image_11,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_11 clicked"),
    relief="flat"
)
button_11.place(
    x=19.0,
    y=784.0,
    width=50.0,
    height=50.0
)

window.resizable(False, False)
window.mainloop()