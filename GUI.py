import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import customtkinter as ctk

import backend as b
import threading

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue") 

class TFTTrackerApp(ctk.CTk):
    def __init__(self):
        self.timer_job = None
        self.game_seconds = 0
        self.base_match_info = ""
        super().__init__()

        self.title("TFT Tracker")
        self.geometry("1100x1000") 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # TYTUŁ GŁÓWNY
        self.title_label = ctk.CTkLabel(self, text="STATYSTYKI", font=ctk.CTkFont(family="Helvetica", size=45, weight="bold"), text_color="#becdd1")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # BUDOWANIE INTERFEJSU
        self.create_left_panel()
        self.create_right_panel()

    def create_left_panel(self):
        """Panel lewy - Szukanie Gracza i Live Game"""
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # SEKCJA WYSZUKIWANIA
        search_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))

        self.entry_name = ctk.CTkEntry(search_frame, width=140, font=("Segoe UI", 12), placeholder_text="Nick")
        self.entry_name.pack(side="left", padx=5)
        self.entry_name.insert(0, "Bartix117")

        ctk.CTkLabel(search_frame, text="#", font=("Segoe UI", 14, "bold"), text_color="#aaa").pack(side="left")

        self.entry_tag = ctk.CTkEntry(search_frame, width=70, font=("Segoe UI", 12), placeholder_text="Tag")
        self.entry_tag.pack(side="left", padx=5)
        self.entry_tag.insert(0, "EUNE")

        region_list = list(b.REGION_MAP.keys()) if hasattr(b, 'REGION_MAP') else ["EUNE", "EUW", "NA"]
        self.region_combo = ctk.CTkOptionMenu(search_frame, values=region_list, width=80)
        self.region_combo.set("EUNE")
        self.region_combo.pack(side="left", padx=10)

        # PRZYCISK WYSZUKAJ
        self.btn_search = ctk.CTkButton(self.left_frame, text="Wyszukaj gracza", font=ctk.CTkFont(size=14), command=self.get_puuid)
        self.btn_search.pack(anchor="w", padx=5, pady=(5, 10))

        #PRZYCISKI TRYBÓW
        modes_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        modes_frame.pack(anchor="w", pady=5)

        self.btn_solo = ctk.CTkButton(modes_frame, text="Solo", width=100, fg_color="#444", hover_color="#555", command=self.show_solo)
        self.btn_solo.pack(side="left", padx=5)

        self.btn_double = ctk.CTkButton(modes_frame, text="Double Up", width=100, fg_color="#444", hover_color="#555", command=self.show_double)
        self.btn_double.pack(side="left", padx=5)

        # STATYSTYKI GRACZA
        self.Stats = ctk.CTkLabel(self.left_frame, text="Zaczekaj na dane...", font=ctk.CTkFont(size=14, weight="bold"), text_color="#becdd1")
        self.Stats.pack(anchor="w", padx=10, pady=20)

        # MIEJSCE NA SZCZEGÓŁY KOMPOZYCJI
        self.comp_frame = ctk.CTkFrame(self.left_frame, fg_color="#1e1e1e", corner_radius=10)
        self.comp_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.comp_frame, text="[Kliknij kompozycję na liście]", text_color="#777").pack(expand=True)

        # LIVE GAME
        live_frame = ctk.CTkFrame(self.left_frame, corner_radius=10, fg_color="#2b1111") # Lekko czerwonawy odcień tła
        live_frame.pack(fill="x", pady=10)

        self.match_stats = ctk.CTkLabel(live_frame, text="Brak danych o grze.", font=ctk.CTkFont(size=13), text_color="#becdd1")
        self.match_stats.pack(pady=(15, 10))

        self.btn_live = ctk.CTkButton(live_frame, text="🔴 SPRAWDŹ LIVE GAME", font=ctk.CTkFont(weight="bold"), 
                                      fg_color="#800000", hover_color="#a00000", command=self.check_live_game)
        self.btn_live.pack(pady=(0, 15), padx=20, fill="x")

    def create_right_panel(self):
        """Panel prawy - Lista Kompozycji"""
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)

        # PASEK POSTĘPU 
        self.progressbar = ctk.CTkProgressBar(self.right_frame, mode="indeterminate")
        self.progressbar.pack(fill="x", padx=20, pady=(20, 5))
        self.progressbar.set(0)
        self.progressbar.pack_forget() # Na start ukrywamy

        #  PRZYCISK ODŚWIEŻANIA
        self.btn_refresh_comp = ctk.CTkButton(self.right_frame, text="Odśwież dane o kompozycjach", font=ctk.CTkFont(size=14), command=self.refresh_data)
        self.btn_refresh_comp.pack(fill="x", padx=20, pady=(10, 10))

        # LISTA
        list_container = ctk.CTkFrame(self.right_frame)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        scrollbar = ctk.CTkScrollbar(list_container)
        scrollbar.pack(side="right", fill="y")

        self.listbox_meta = tk.Listbox(list_container, font=("Segoe UI", 12), bg="#1e1e1e", fg="white",
                                       selectbackground="#ff5555", selectforeground="white", 
                                       bd=0, highlightthickness=0, yscrollcommand=scrollbar.set)
        self.listbox_meta.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.configure(command=self.listbox_meta.yview)

        
        self.listbox_meta.bind('<<ListboxSelect>>', self.comp_select)

    def start_live_timer(self):
        
        self.game_seconds += 1
        
        m, s = divmod(self.game_seconds, 60)
        time_str = f"{m}:{s:02d}"

        full_text = f" Czas: {time_str}\n\n{self.base_match_info}"
        self.match_stats.configure(text=full_text)
        
        self.timer_job = self.after(1000, self.start_live_timer)

    def stop_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    def silent_validation(self):
        try:
            status = b.fetch_match_data()
            
            if status == "Nie_w_grze":

                self.stop_timer() 
                self.match_stats.configure(text="GRA ZAKOŃCZONA", text_color="orange")
                self.btn_live.configure(state="normal")       
            elif status == "W_grze":
                real_seconds = b.get_game_seconds()
                if real_seconds > 0:
                    if abs(self.game_seconds - real_seconds) > 5:
                        self.game_seconds = real_seconds
                        print(f"[SYNC] Skorygowano czas o {abs(self.game_seconds - real_seconds)}s")

        except Exception as e:
            print(f"Błąd weryfikacji w tle: {e}")

        if self.timer_job is not None:
            self.after(30000, lambda: threading.Thread(target=self.silent_validation).start())

    def get_puuid(self):
        b.game_name = self.entry_name.get()
        b.game_tag = self.entry_tag.get()
        b.selected_region=self.region_combo.get()
        region=b.REGION_MAP[b.selected_region]["region"]
        puuid_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{b.game_name}/{b.game_tag}?"
        print(f"Pytam o: {b.game_name}/{b.game_tag}...")
        response = b.requests.get(puuid_url, params={"api_key": b.api_key})
        if response.status_code == 200:
            data = response.json()
            print(response.json())
            b.current_puuid=data['puuid']
            b.fetch_data()
        #    show_stats()
        else:
            print(f"Błąd: {response.status_code}")
            

    # def show_stats():
    #     tft_entry = None
    #     for entry in b.user_data:
    #         q_type = entry.get('queueType')
    #         if q_type == 'RANKED_TFT':
    #             tft_entry = entry
    #             break
    #     if tft_entry:
    #         tier = tft_entry.get('tier', 'Unknown')
    #         rank = tft_entry.get('rank', '')
    #         lp = tft_entry.get('leaguePoints', 0)
    #         wins = tft_entry.get('wins', 0)
    #         losses = tft_entry.get('losses', 0)
    #         Stats.configure(text=(f"Tryb: TFT\n"
    #                 f"Ranga: {tier} {rank}\n"
    #                 f"LP: {lp}\n"
    #                 f"W: {wins} / L: {losses}"))
    #         return
    #     else:
    #         return (f"Gracz znaleziony,\n"
    #         " ale jest UNRANKED w TFT.")

    def show_solo(self):
        tekst = b.get_stats_by_queue('RANKED_TFT')
        self.Stats.configure(text=tekst)

    def check_live_game(self):
        self.match_stats.configure(text="Sprawdzam, czy gracz jest w meczu...")
        
        self.btn_live.configure(state="disabled")
        threading.Thread(target=self.run_thread).start()

    def run_thread(self):
        status = b.fetch_match_data()

        self.stop_timer()

        if status == "W_grze":
            self.game_seconds = b.get_game_seconds()
            self.base_match_info = b.get_live_game_text()
            self.start_live_timer()
            self.after(30000, lambda: threading.Thread(target=self.silent_validation).start())
        elif status == "Nie_w_grze":
            self.match_stats.configure(text="Gracz aktualnie NIE jest w grze.")
        else:
            self.match_stats.configure(text="Błąd połączenia z serwerem Live.")
                
        self.btn_live.configure(state="normal")


    def show_double(self):
        tekst = b.get_stats_by_queue('RANKED_TFT_DOUBLE_UP')
        self.Stats.configure(text=tekst)

    def refresh_data(self):
        self.btn_refresh_comp.configure(text="Aktualizowanie...", state="disabled")
        self.progressbar.pack(fill="x", padx=20, pady=(5, 5), before=self.btn_refresh_comp)
        self.progressbar.start()
        threading.Thread(target=self.run_refresh_thread).start()

    def run_refresh_thread(self):
        meta_text = b.fetch_data_comps()
        self.listbox_meta.delete(0, tk.END)
        for c in b.global_comps_data:
           
            strat_info = f"({c['strategy']})" if c['strategy'] else ""
            self.listbox_meta.insert(tk.END, f"{c['id']}. [{c['tier']}] {c['name']} {strat_info}")

        
        self.progressbar.stop()
        self.progressbar.pack_forget()
            
            
        self.btn_refresh_comp.configure(text="Odśwież dane o kompozycjach", state="normal")

    def comp_select(self,event):
        selection = self.listbox_meta.curselection()
        if not selection:
            return
        
        index = selection[0]
        
        if index < len(b.global_comps_data):
            comp = b.global_comps_data[index]
            self.open_comp(comp)

    def open_comp(self,comp):
        for widget in self.comp_frame.winfo_children():
            widget.destroy()
        header_text = f"[{comp['tier']}] {comp['name']}"
        ctk.CTkLabel(self.comp_frame, text=header_text, font=ctk.CTkFont(family="Arial", size=18, weight="bold"),text_color="gold").pack(pady=10)
        if comp['strategy']:
                ctk.CTkLabel(self.comp_frame, text=f"Styl: {comp['strategy']}", font=ctk.CTkFont(family="Arial", size=12, slant="italic"), text_color="#88ff88").pack(pady=0)
            
        ctk.CTkLabel(self.comp_frame, text="--- SKŁAD ---", font=ctk.CTkFont(family="Arial", size=14), text_color="#aaa").pack(pady=10)
            
        
        for champ in comp['champs']:
            ctk.CTkLabel(self.comp_frame, text=champ, font=ctk.CTkFont(family="Segoe UI", size=16), text_color="white").pack(anchor="center")



if __name__ == "__main__":
    app = TFTTrackerApp()
    app.mainloop()