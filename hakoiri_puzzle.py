import heapq

# ピースのID定義
EM = 0  # 空きマス
MP = 1  # 箱入り娘

# 横2マスブロック
H1 = 2
H2 = 3
H3 = 4
H4 = 5

# 縦2マスブロック
V1 = 6
V2 = 7
V3 = 8
V4 = 9

# 1x1ブロック
S1 = 10
S2 = 11
S3 = 12
S4 = 13

# ピースの属性
PIECE_PROPERTIES = {
    MP: {'width': 2, 'height': 2, 'name': 'MP', 'color': '#FF6B6B'},
    H1: {'width': 2, 'height': 1, 'name': 'H1', 'color': '#4ECDC4'},
    H2: {'width': 2, 'height': 1, 'name': 'H2', 'color': '#4ECDC4'},
    H3: {'width': 2, 'height': 1, 'name': 'H3', 'color': '#4ECDC4'},
    H4: {'width': 2, 'height': 1, 'name': 'H4', 'color': '#4ECDC4'},
    V1: {'width': 1, 'height': 2, 'name': 'V1', 'color': '#45B7D1'},
    V2: {'width': 1, 'height': 2, 'name': 'V2', 'color': '#45B7D1'},
    V3: {'width': 1, 'height': 2, 'name': 'V3', 'color': '#45B7D1'},
    V4: {'width': 1, 'height': 2, 'name': 'V4', 'color': '#45B7D1'},
    S1: {'width': 1, 'height': 1, 'name': 'S1', 'color': '#96CEB4'},
    S2: {'width': 1, 'height': 1, 'name': 'S2', 'color': '#96CEB4'},
    S3: {'width': 1, 'height': 1, 'name': 'S3', 'color': '#96CEB4'},
    S4: {'width': 1, 'height': 1, 'name': 'S4', 'color': '#96CEB4'},
}

class HakoiriPuzzle:
    def __init__(self, board_height=5, board_width=4):
        self.BOARD_HEIGHT = board_height
        self.BOARD_WIDTH = board_width
        self.GOAL_MAIN_PIECE_ROW = 3
        self.GOAL_MAIN_PIECE_COL_START = 1
        self.GOAL_MAIN_PIECE_COL_END = 1
        
        # デフォルトの初期盤面
        self.initial_board = [
            [V1, MP, MP, S1],
            [V1, MP, MP, S2], 
            [V2, V3, V4, S3],
            [V2, V3, V4, S4],
            [EM, H1, H1, EM]
        ]
        
    def set_initial_board(self, board):
        """初期盤面を設定"""
        self.initial_board = board
        
    def find_piece_top_left(self, board, piece_id):
        """指定されたピースIDの左上隅の座標を見つける"""
        for r in range(self.BOARD_HEIGHT):
            for c in range(self.BOARD_WIDTH):
                if board[r][c] == piece_id:
                    return (r, c)
        return None
        
    def is_valid_move(self, board, piece_id, current_pos, new_pos, width, height):
        """ピースが新しい位置に移動できるかチェック"""
        new_r, new_c = new_pos
        
        if not (0 <= new_r < self.BOARD_HEIGHT and 0 <= new_c < self.BOARD_WIDTH and
                0 <= new_r + height - 1 < self.BOARD_HEIGHT and 0 <= new_c + width - 1 < self.BOARD_WIDTH):
            return False
            
        for r_offset in range(height):
            for c_offset in range(width):
                check_r, check_c = new_r + r_offset, new_c + c_offset
                if board[check_r][check_c] != EM and board[check_r][check_c] != piece_id:
                    return False
        return True
        
    def get_all_possible_moves(self, board):
        """現在の盤面から有効なすべての移動を生成"""
        moves = []
        unique_pieces_on_board = set()
        
        for r in range(self.BOARD_HEIGHT):
            for c in range(self.BOARD_WIDTH):
                if board[r][c] != EM:
                    unique_pieces_on_board.add(board[r][c])
                    
        for piece_id in unique_pieces_on_board:
            current_pos = self.find_piece_top_left(board, piece_id)
            if current_pos is None:
                continue
                
            current_r, current_c = current_pos
            width = PIECE_PROPERTIES[piece_id]['width']
            height = PIECE_PROPERTIES[piece_id]['height']
            piece_name = PIECE_PROPERTIES[piece_id]['name']
            
            for dr, dc, direction_name in [(0, 1, "右"), (0, -1, "左"), (1, 0, "下"), (-1, 0, "上")]:
                new_r, new_c = current_r + dr, current_c + dc
                
                if self.is_valid_move(board, piece_id, (current_r, current_c), (new_r, new_c), width, height):
                    new_board = [row[:] for row in board]
                    
                    # 元の場所を空にする
                    for r_offset in range(height):
                        for c_offset in range(width):
                            new_board[current_r + r_offset][current_c + c_offset] = EM
                            
                    # 新しい場所にピースを置く
                    for r_offset in range(height):
                        for c_offset in range(width):
                            new_board[new_r + r_offset][new_c + c_offset] = piece_id
                            
                    moves.append((new_board, f"ピース{piece_name}を{direction_name}に移動"))
        return moves
        
    def is_goal(self, board):
        """現在の盤面がゴール状態かチェック"""
        main_piece_pos = self.find_piece_top_left(board, MP)
        if not main_piece_pos:
            return False
            
        main_r, main_c = main_piece_pos
        return (main_r >= self.GOAL_MAIN_PIECE_ROW and
                self.GOAL_MAIN_PIECE_COL_START <= main_c <= self.GOAL_MAIN_PIECE_COL_END)
                
    def calculate_heuristic(self, board):
        """ヒューリスティック関数"""
        main_piece_pos = self.find_piece_top_left(board, MP)
        if not main_piece_pos:
            return float('inf')
            
        main_r, main_c = main_piece_pos
        main_h = PIECE_PROPERTIES[MP]['height']
        main_w = PIECE_PROPERTIES[MP]['width']
        
        h1 = max(0, self.GOAL_MAIN_PIECE_ROW - main_r)
        
        blocks_below_main = 0
        if main_r + main_h < self.BOARD_HEIGHT:
            for c_offset in range(main_w):
                if board[main_r + main_h][main_c + c_offset] != EM:
                    if board[main_r + main_h][main_c + c_offset] != MP:
                        blocks_below_main += 1
                        
        blocks_in_goal_path = 0
        for r in range(main_r + main_h, self.BOARD_HEIGHT):
            for c in range(main_c, main_c + main_w):
                if board[r][c] != EM and board[r][c] != MP:
                    blocks_in_goal_path += 1
                    
        if not (self.GOAL_MAIN_PIECE_COL_START <= main_c <= self.GOAL_MAIN_PIECE_COL_END):
            target_col = self.GOAL_MAIN_PIECE_COL_START
            if main_c < target_col:
                for r_offset in range(main_h):
                    for c in range(main_c + main_w, target_col + main_w):
                        if c < self.BOARD_WIDTH and board[main_r + r_offset][c] != EM:
                            blocks_in_goal_path += 1
            elif main_c > target_col:
                for r_offset in range(main_h):
                    for c in range(target_col, main_c):
                        if c >= 0 and board[main_r + r_offset][c] != EM:
                            blocks_in_goal_path += 1
                            
        return h1 + blocks_below_main + blocks_in_goal_path
        
class State:
    def __init__(self, board, g_cost, puzzle, parent=None, move=None):
        self.board = board
        self.g_cost = g_cost
        self.parent = parent
        self.move = move
        self.h_cost = puzzle.calculate_heuristic(board)
        self.f_cost = self.g_cost + self.h_cost
        
    def __lt__(self, other):
        return self.f_cost < other.f_cost
        
    def __hash__(self):
        return hash(tuple(map(tuple, self.board)))
        
    def __eq__(self, other):
        return self.board == other.board

class HakoiriSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.progress_callback = None
        self.stop_flag_func = None
        
    def set_progress_callback(self, callback):
        """進捗表示用のコールバック関数を設定"""
        self.progress_callback = callback
        
    def set_stop_flag_function(self, stop_flag_func):
        """中止フラグをチェックする関数を設定"""
        self.stop_flag_func = stop_flag_func
        
    def solve_astar(self):
        """A*アルゴリズムで解を探索（Web進捗表示付き）"""
        initial_state = State(self.puzzle.initial_board, 0, self.puzzle)
        
        open_set = [(initial_state.f_cost, initial_state)]
        closed_set = {hash(initial_state): initial_state.g_cost}
        
        explored_count = 0
        progress_interval = 1000  # 1000回ごとに進捗表示
        
        while open_set:
            # 中止フラグをチェック
            if self.stop_flag_func and self.stop_flag_func():
                return None  # 中止された場合はNoneを返す
                
            f_cost, current_state = heapq.heappop(open_set)
            explored_count += 1
            
            # Web画面への進捗表示（コンソールには出力しない）
            if explored_count % progress_interval == 0 and self.progress_callback:
                progress_info = {
                    'explored_count': explored_count,
                    'current_moves': current_state.g_cost,
                    'estimated_remaining': current_state.h_cost
                }
                self.progress_callback(progress_info)
            
            if current_state.g_cost > closed_set.get(hash(current_state), float('inf')):
                continue
                
            if self.puzzle.is_goal(current_state.board):
                path_states = []
                temp_state = current_state
                while temp_state:
                    path_states.append(temp_state)
                    temp_state = temp_state.parent
                
                # 最終結果もWeb画面に通知
                if self.progress_callback:
                    final_info = {
                        'solved': True,
                        'total_explored': explored_count,
                        'final_moves': len(path_states) - 1
                    }
                    self.progress_callback(final_info)
                    
                return path_states[::-1]
                
            for next_board, move_description in self.puzzle.get_all_possible_moves(current_state.board):
                next_g_cost = current_state.g_cost + 1
                next_state = State(next_board, next_g_cost, self.puzzle, current_state, move_description)
                
                if hash(next_state) not in closed_set or next_g_cost < closed_set[hash(next_state)]:
                    closed_set[hash(next_state)] = next_g_cost
                    heapq.heappush(open_set, (next_state.f_cost, next_state))
        
        # 解が見つからない場合もWeb画面に通知
        if self.progress_callback:
            final_info = {
                'solved': False,
                'total_explored': explored_count
            }
            self.progress_callback(final_info)
            
        return None