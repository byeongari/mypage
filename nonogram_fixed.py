import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import random
import time

class NonogramGame:
    def __init__(self, master):
        self.master = master
        self.master.title("노노그램 게임")
        
        # 창 크기 조절 허용
        self.master.resizable(True, True)

        # 캔버스 생성
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 버튼 프레임 생성
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack()

        # 정답 보기 버튼 추가
        self.show_answer_button = tk.Button(self.button_frame, text="정답 보기", command=self.show_solution)
        self.show_answer_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 창 크기 변경 이벤트 바인딩
        self.master.bind('<Configure>', self.on_window_resize)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # 게임 초기화
        self.create_game()

    def create_game(self):
        # 기존 게임 데이터 초기화
        self.canvas.delete("all")
        self.user_grid = []
        self.solution = []
        self.row_hints = []
        self.col_hints = []

        self.size = self.get_grid_size()
        if not self.size:
            sys.exit()

        self.solution = self.generate_puzzle(self.size)
        self.row_hints = self.get_hints_from_grid(self.solution)
        self.col_hints = self.get_hints_from_grid(list(map(list, zip(*self.solution))))
        self.user_grid = [[0]*self.size for _ in range(self.size)]

        # 그리드 초기화
        self.cell_size = 30  # 초기 셀 크기
        self.margin_x = 50   # 초기 여백
        self.margin_y = 50

        # 타이머 시작
        self.start_time = time.time()

        self.draw_grid()

    def get_grid_size(self):
        while True:
            try:
                size = simpledialog.askinteger("그리드 크기", "그리드 크기를 입력하세요 (6에서 20 사이의 정수):", minvalue=6, maxvalue=20)
                if size:
                    return size
                else:
                    return None
            except ValueError:
                messagebox.showerror("입력 오류", "유효한 정수를 입력해주세요.")

    def generate_puzzle(self, size):
        # 랜덤으로 퍼즐 생성
        grid = [[random.choice([0, 1]) for _ in range(size)] for _ in range(size)]
        return grid

    def get_hints_from_grid(self, grid):
        hints = []
        for line in grid:
            hint = []
            count = 0
            for cell in line:
                if cell == 1:
                    count += 1
                elif count > 0:
                    hint.append(count)
                    count = 0
            if count > 0:
                hint.append(count)
            if not hint:
                hint = [0]
            hints.append(hint)
        return hints

    def draw_grid(self):
        self.canvas.delete("all")

        # 캔버스 크기 가져오기
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 셀 크기 및 여백 계산
        max_cell_width = (canvas_width - 150) / self.size  # 힌트 영역 고려
        max_cell_height = (canvas_height - 150) / self.size
        self.cell_size = min(max_cell_width, max_cell_height, 50)  # 최대 셀 크기 제한
        self.margin_x = (canvas_width - (self.cell_size * self.size)) / 2
        self.margin_y = (canvas_height - (self.cell_size * self.size)) / 2

        # 힌트 폰트 크기 계산
        self.hint_font_size = int(self.cell_size * 0.4)
        if self.hint_font_size < 8:
            self.hint_font_size = 8
        elif self.hint_font_size > 20:
            self.hint_font_size = 20
        self.hint_font = ("Arial", self.hint_font_size)

        # 그리드 그리기
        for i in range(self.size):
            for j in range(self.size):
                x0 = self.margin_x + j * self.cell_size
                y0 = self.margin_y + i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                color = "white"
                if self.user_grid[i][j] == 1:
                    color = "black"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black", tags=f"cell_{i}_{j}")
        self.draw_hints()

    def draw_hints(self):
        # 힌트 지우기
        self.canvas.delete("hint")

        # 행 힌트 표시
        for i, hints in enumerate(self.row_hints):
            hint_text = ' '.join(map(str, hints))
            x = self.margin_x - 10
            y = self.margin_y + i * self.cell_size + self.cell_size / 2
            self.canvas.create_text(x, y, text=hint_text, anchor="e", font=self.hint_font, tags="hint")
        # 열 힌트 표시
        for j, hints in enumerate(self.col_hints):
            hint_text = '\n'.join(map(str, hints))
            x = self.margin_x + j * self.cell_size + self.cell_size / 2
            y = self.margin_y - 10
            self.canvas.create_text(x, y, text=hint_text, anchor="s", font=self.hint_font, tags="hint")

    def on_canvas_click(self, event):
        x = event.x
        y = event.y

        j = int((x - self.margin_x) // self.cell_size)
        i = int((y - self.margin_y) // self.cell_size)
        if 0 <= i < self.size and 0 <= j < self.size:
            self.user_grid[i][j] = 1 if self.user_grid[i][j] == 0 else 0
            self.draw_grid()
            if self.check_puzzle():
                self.show_completion_dialog()

    def check_puzzle(self):
        # 사용자의 그리드로부터 힌트 생성
        user_row_hints = self.get_hints_from_grid(self.user_grid)
        user_col_hints = self.get_hints_from_grid(list(map(list, zip(*self.user_grid))))

        # 원래 힌트와 비교
        return user_row_hints == self.row_hints and user_col_hints == self.col_hints

    def show_completion_dialog(self):
        # 타이머 종료 및 경과 시간 계산
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        result = messagebox.askquestion(
            "퍼즐 완료",
            f"축하합니다! 퍼즐을 완성하셨습니다.\n소요 시간: {minutes}분 {seconds}초\n다시 플레이하시겠습니까?"
        )
        if result == 'yes':
            self.create_game()
        else:
            self.master.quit()

    def on_window_resize(self, event):
        # 창 크기 변경 시 그리드 다시 그리기
        if event.widget == self.master:
            self.draw_grid()

    def show_solution(self):
        # 정답을 사용자 그리드에 복사
        self.user_grid = [row[:] for row in self.solution]
        self.draw_grid()
        messagebox.showinfo("정답 보기", "정답이 표시되었습니다.")

        # 게임을 종료하거나 다시 시작할 수 있도록 처리
        result = messagebox.askquestion("게임 종료", "새로운 게임을 시작하시겠습니까?")
        if result == 'yes':
            self.create_game()
        else:
            self.master.quit()

def main():
    root = tk.Tk()
    game = NonogramGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
