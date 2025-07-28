import heapq
from copy import deepcopy

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
        
        # デフォルトの初期盤面（確実に解ける標準配置・約30手）
        self.initial_board = [
            [S3, H3, H3, S4],
            [V1, MP, MP, V2],
            [V1, MP, MP, V2], 
            [S1, H1, H1, S2],
            [EM, H2, H2, EM]
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
                
            prop = PIECE_PROPERTIES[piece_id]
            width, height = prop['width'], prop['height']
            current_r, current_c = current_pos
            
            # 上下左右の移動を試す
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                new_r, new_c = current_r + dr, current_c + dc
                
                if self.is_valid_move(board, piece_id, current_pos, (new_r, new_c), width, height):
                    new_board = self.apply_move(board, piece_id, current_pos, (new_r, new_c), width, height)
                    move_description = f"{prop['name']}を({current_r},{current_c})から({new_r},{new_c})へ移動"
                    moves.append((new_board, move_description))
                    
        return moves
        
    def apply_move(self, board, piece_id, old_pos, new_pos, width, height):
        """ピースを移動させた新しい盤面を生成"""
        new_board = deepcopy(board)
        old_r, old_c = old_pos
        new_r, new_c = new_pos
        
        # 古い位置をクリア
        for r_offset in range(height):
            for c_offset in range(width):
                new_board[old_r + r_offset][old_c + c_offset] = EM
                
        # 新しい位置に配置
        for r_offset in range(height):
            for c_offset in range(width):
                new_board[new_r + r_offset][new_c + c_offset] = piece_id
                
        return new_board
        
    def is_goal(self, board):
        """ゴール判定：箱入り娘が目標位置にあるかチェック"""
        goal_r, goal_c = self.GOAL_MAIN_PIECE_ROW, self.GOAL_MAIN_PIECE_COL_START
        return (board[goal_r][goal_c] == MP and board[goal_r][goal_c + 1] == MP and
                board[goal_r + 1][goal_c] == MP and board[goal_r + 1][goal_c + 1] == MP)
                
    def calculate_manhattan_distance(self, board):
        """マンハッタン距離ヒューリスティック"""
        mp_pos = self.find_piece_top_left(board, MP)
        if mp_pos is None:
            return float('inf')
            
        goal_r, goal_c = self.GOAL_MAIN_PIECE_ROW, self.GOAL_MAIN_PIECE_COL_START
        current_r, current_c = mp_pos
        return abs(current_r - goal_r) + abs(current_c - goal_c)

class State:
    def __init__(self, board, g_cost, puzzle, parent=None, move=''):
        self.board = board
        self.g_cost = g_cost
        self.h_cost = puzzle.calculate_manhattan_distance(board)
        self.f_cost = g_cost + self.h_cost
        self.parent = parent
        self.move = move
        
    def __lt__(self, other):
        if self.f_cost != other.f_cost:
            return self.f_cost < other.f_cost
        return self.h_cost < other.h_cost
        
    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

class HakoiriSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.progress_callback = None
        self.stop_flag_function = None
        self.total_explored = 0
        
    def set_progress_callback(self, callback):
        """進捗コールバック関数を設定"""
        self.progress_callback = callback
        
    def set_stop_flag_function(self, stop_func):
        """中止フラグチェック関数を設定"""
        self.stop_flag_function = stop_func
        
    def solve_astar(self):
        """A*アルゴリズムで解を探索（Web進捗表示付き）"""
        initial_state = State(self.puzzle.initial_board, 0, self.puzzle)
        
        open_set = [(initial_state.f_cost, initial_state)]
        closed_set = {hash(initial_state): initial_state.g_cost}
        
        explored_count = 0
        progress_interval = 1000  # 1000回ごとに進捗表示
        
        while open_set:
            # 中止フラグをチェック
            if self.stop_flag_function and self.stop_flag_function():
                break
                
            f_cost, current_state = heapq.heappop(open_set)
            explored_count += 1
            self.total_explored = explored_count
            
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
                next_hash = hash(next_state)
                
                if next_hash in closed_set and next_g_cost >= closed_set[next_hash]:
                    continue
                    
                closed_set[next_hash] = next_g_cost
                heapq.heappush(open_set, (next_state.f_cost, next_state))
        
        # 解が見つからなかった場合
        if self.progress_callback:
            final_info = {
                'solved': False,
                'total_explored': explored_count
            }
            self.progress_callback(final_info)
            
        return None