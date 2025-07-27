from flask import Flask, render_template, jsonify, request, Response
import json
import threading
import time
import queue
from hakoiri_puzzle import HakoiriPuzzle, HakoiriSolver

app = Flask(__name__)

# グローバル変数
puzzle = None
solver = None
solving_thread = None
progress_queue = queue.Queue()
stop_flags = {}  # セッションごとの中止フラグ
current_session_id = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize():
    global puzzle, solver, current_session_id
    
    try:
        data = request.json
        board = data.get('board', [])
        current_session_id = data.get('session_id', 'default')
        
        # 中止フラグをリセット
        stop_flags[current_session_id] = False
        
        # パズルとソルバーを初期化
        puzzle = HakoiriPuzzle()
        puzzle.set_initial_board(board)
        
        solver = HakoiriSolver(puzzle)
        
        # 進捗コールバックを設定
        solver.set_progress_callback(lambda info: progress_queue.put({
            'session_id': current_session_id,
            'type': 'progress',
            **info
        }))
        
        # 中止フラグチェック関数を設定
        solver.set_stop_flag_function(lambda: stop_flags.get(current_session_id, False))
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/solve', methods=['POST'])
def solve():
    global solver, solving_thread, current_session_id
    
    try:
        if not solver:
            return jsonify({'success': False, 'error': 'パズルが初期化されていません'})
        
        if solving_thread and solving_thread.is_alive():
            return jsonify({'success': False, 'error': '既に探索中です'})
        
        # バックグラウンドで解法を実行
        def solve_in_background():
            try:
                solution = solver.solve_astar()
                
                if solution:
                    # 解法完了
                    result_info = {
                        'session_id': current_session_id,
                        'type': 'final_result',
                        'solved': True,
                        'total_steps': len(solution),
                        'solution': [state.board for state in solution]
                    }
                else:
                    # 解なし
                    result_info = {
                        'session_id': current_session_id,
                        'type': 'final_result',
                        'solved': False,
                        'message': '解が見つかりませんでした'
                    }
                
                progress_queue.put(result_info)
                
            except Exception as e:
                error_info = {
                    'session_id': current_session_id,
                    'type': 'error',
                    'error': str(e)
                }
                progress_queue.put(error_info)
        
        solving_thread = threading.Thread(target=solve_in_background, daemon=True)
        solving_thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_solving():
    global current_session_id
    
    try:
        data = request.json or {}
        session_id = data.get('session_id', current_session_id or 'default')
        
        # 中止フラグを設定
        stop_flags[session_id] = True
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/progress')
def progress():
    def generate():
        while True:
            try:
                # ハートビート送信（30秒ごと）
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                
                # キューから進捗データを取得（ノンブロッキング）
                try:
                    while True:
                        progress_data = progress_queue.get_nowait()
                        yield f"data: {json.dumps(progress_data)}\n\n"
                except queue.Empty:
                    pass
                
                time.sleep(1)  # 1秒間隔で送信
                
            except GeneratorExit:
                break
            except Exception as e:
                error_data = {'type': 'error', 'error': str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/validate_board', methods=['POST'])
def validate_board():
    try:
        data = request.json
        board = data.get('board', [])
        
        # 基本的な盤面チェック
        if len(board) != 5 or any(len(row) != 4 for row in board):
            return jsonify({'valid': False, 'error': '盤面サイズが正しくありません'})
        
        # MPの存在チェック
        mp_count = sum(row.count(1) for row in board)
        if mp_count != 4:
            return jsonify({'valid': False, 'error': '箱入り娘(MP)は4マス必要です'})
        
        return jsonify({'valid': True})
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)