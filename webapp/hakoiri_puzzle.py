        self.progress_callback = callback
        
    def solve_astar(self):
        """A*アルゴリズムで解を探索（Web進捗表示付き）"""
        initial_state = State(self.puzzle.initial_board, 0, self.puzzle)
        
        open_set = [(initial_state.f_cost, initial_state)]
        closed_set = {hash(initial_state): initial_state.g_cost}
        
        explored_count = 0
        progress_interval = 1000  # 1000回ごとに進捗表示
        
        while open_set:
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
                