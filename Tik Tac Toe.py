import os
import requests
import customtkinter as ctk
from tkinter import messagebox

# replace with your own rgoq api key
GROQ_API_KEY = ""

player_score = 0
ai_score = 0

# asks groq for moves
def query_groq(board_state, valid_moves):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # turn reply into string
    valid_moves_str = ", ".join([f"({row},{col})" for row, col in valid_moves])
    
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are an AI that plays Tic-Tac-Toe. Respond with the best move as a board position in the form (row,col) from the list of valid moves. Do not reply with anything other than (row,col)"},
            {"role": "user", "content": f"Current board state:\n{board_state}\nValid moves are: {valid_moves_str}\nWhere should 'O' play next?"}
        ]
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        ai_move = response.json()["choices"][0]["message"]["content"]
        print(f"AI move response: {ai_move}")
        return ai_move
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Oops! Something went wrong."

# check win/draw
def check_winner():
    #win
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] != "":
            return board[row][0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != "":
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "":
        return board[0][2]
    #draw
    if all(board[row][col] != "" for row in range(3) for col in range(3)):
        return "draw"
    
    return None 

# restart game
def start_over():
    global board, buttons, game_over, player_score, ai_score, score_label
    # Reset the game state
    board = [["" for _ in range(3)] for _ in range(3)]
    game_over = False
    
    # reset the board UI
    for row in range(3):
        for col in range(3):
            buttons[row][col].configure(text="", state="normal")
    
    # update score
    score_label.configure(text=f"Player: {player_score} - AI: {ai_score}")

# everymove change the board
def make_move(row, col):
    global game_over, player_score, ai_score
    
    if game_over:
        return  
    
    if board[row][col] == "":
        # player move
        board[row][col] = "X"
        buttons[row][col].configure(text="X", state="disabled")
        
        winner = check_winner()
        if winner:
            if winner == "X":
                player_score += 1
                messagebox.showinfo("Game Over", "You win!")
            elif winner == "O":
                ai_score += 1
                messagebox.showinfo("Game Over", "AI wins!")
            else:
                messagebox.showinfo("Game Over", "It's a draw!")
            game_over = True  
            show_start_over_popup()  
            return  
        
        # ai move
        board_state = "\n".join([" ".join(row) for row in board])
        
        # make valid lists for ai 
        valid_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ""]
        
        # ask ai until valid move
        while True:
            ai_move = query_groq(board_state, valid_moves)
            
            try:
                ai_move = ai_move.strip()
                if ai_move.startswith("(") and ai_move.endswith(")"):
                    ai_move = ai_move[1:-1]  # remove parentheses
                ai_row, ai_col = map(int, ai_move.split(","))
                
                if (ai_row, ai_col) in valid_moves:
                    board[ai_row][ai_col] = "O"
                    buttons[ai_row][ai_col].configure(text="O", state="disabled")
                    break  
                else:
                    messagebox.showwarning("Invalid AI Move", "AI gave an invalid move. Trying again...")
            except Exception as e:
                messagebox.showwarning("Invalid AI Move", f"Failed to parse AI's move. Trying again...\n{str(e)}")
        
        winner = check_winner()
        if winner:
            if winner == "X":
                player_score += 1
                messagebox.showinfo("Game Over", "You win!")
            elif winner == "O":
                ai_score += 1
                messagebox.showinfo("Game Over", "AI wins!")
            else:
                messagebox.showinfo("Game Over", "It's a draw!")
            game_over = True  
            show_start_over_popup()  
            return  

# start game over
def show_start_over_popup():
    response = messagebox.askquestion("Game Over", "Do you want to start a new game?", icon='info')
    if response == "yes":
        start_over()  

# GUI Setup
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("400x500")
app.title("Tic-Tac-Toe vs AI")

#init board
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []
game_over = False

frame = ctk.CTkFrame(app)
frame.pack(pady=20)


score_label = ctk.CTkLabel(app, text=f"Player: {player_score} - AI: {ai_score}", font=("Arial", 18))
score_label.pack(pady=10)

for i in range(3):
    row_buttons = []
    for j in range(3):
        btn = ctk.CTkButton(frame, text="", width=100, height=100, font=("Arial", 24), command=lambda i=i, j=j: make_move(i, j))
        btn.grid(row=i, column=j, padx=5, pady=5)
        row_buttons.append(btn)
    buttons.append(row_buttons)


app.mainloop()
