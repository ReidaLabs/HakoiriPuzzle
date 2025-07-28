from flask import Flask, render_template, request, jsonify, session, Response
from hakoiri_puzzle import HakoiriPuzzle, HakoiriSolver, PIECE_PROPERTIES
import json
import threading
import time
import queue
import uuid

app = Flask(__name__)
app.secret_key = '***REMOVED***'

# グローバル進捗キューと解結果保存
progress_queues = {}
solution_cache = {}
stop_flags = {}  # 探索中止フラグ

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize_puzzle():
    """パズルを初期化"""
    data = request.get_json()
    board = data.get('board')
    
    puzzle = HakoiriPuzzle()
    if board:
        puzzle.set_initial_board(board)
    
    # セッションにパズルの初期状態を保存
    session['initial_board'] = puzzle.initial_board
    session['current_step'] = 0
    session['solution'] = None
    
    return jsonify({
        'success': True,
        'board': puzzle.initial_board,
        'piece_properties': PIECE_PROPERTIES
    })

def create_progress_callback(session_id):
    """進捗コールバック関数を作成"""
    def progress_callback(info):
        if session_id in progress_queues:
            try:
                progress_queues[session_id].put_nowait(info)
            except queue.Full:
                # キューが満杯の場合は古いデータを1つ削除してから追加
                try:
                    progress_queues[session_id].get_nowait()
                    progress_queues[session_id].put_nowait(info)
                except queue.Empty:
                    pass
    return progress_callback

@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
    """パズルを解く（リアルタイム進捗表示付き）"""
    if 'initial_board' not in session:
        return jsonify({'success': False, 'error': 'パズルが初期化されていません'})
    
    # ユニークなセッションIDを生成
    session_id = str(uuid.uuid4())
    session['task_id'] = session_id
    progress_queues[session_id] = queue.Queue(maxsize=50)
    stop_flags[session_id] = False
    
    # 初期盤面をコピー（バックグラウンドスレッド用）
    initial_board = [row[:] for row in session['initial_board']]
    
    puzzle = HakoiriPuzzle()
    puzzle.set_initial_board(initial_board)
    
    solver = HakoiriSolver(puzzle)
    solver.set_progress_callback(create_progress_callback(session_id))
    
    # 中止フラグチェック関数をソルバーに設定
    solver.set_stop_flag_function(lambda: stop_flags.get(session_id, False))
    
    def solve_in_background():
        try:
            solution = solver.solve_astar()
            
            if solution:
                # 解をグローバルキャッシュに保存
                solution_data = [{'board': state.board, 'move': state.move} for state in solution]
                solution_cache[session_id] = {
                    'solution': solution_data,
                    'current_step': 0
                }
                
                # 最終結果を進捗キューに追加
                final_result = {
                    'type': 'final_result',
                    'success': True,
                    'total_steps': len(solution) - 1,
                    'total_explored': getattr(solver, 'total_explored', 0)
                }
            else:
                final_result = {
                    'type': 'final_result',
                    'success': False,
                    'total_explored': getattr(solver, 'total_explored', 0)
                }
                
            # 安全にキューに追加
            if session_id in progress_queues:
                try:
                    progress_queues[session_id].put_nowait(final_result)
                except queue.Full:
                    try:
                        progress_queues[session_id].get_nowait()
                        progress_queues[session_id].put_nowait(final_result)
                    except queue.Empty:
                        pass
                        
        except Exception as e:
            error_result = {
                'type': 'final_result',
                'success': False,
                'error': f'解決中にエラーが発生しました: {str(e)}'
            }
            if session_id in progress_queues:
                try:
                    progress_queues[session_id].put_nowait(error_result)
                except queue.Full:
                    try:
                        progress_queues[session_id].get_nowait()
                        progress_queues[session_id].put_nowait(error_result)
                    except queue.Empty:
                        pass
    
    # バックグラウンドで解を探索
    thread = threading.Thread(target=solve_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': '解探索を開始しました',
        'session_id': session_id
    })

@app.route('/api/stop', methods=['POST'])
def stop_solving():
    """探索を中止"""
    task_id = session.get('task_id')
    if task_id and task_id in stop_flags:
        stop_flags[task_id] = True
        return jsonify({'success': True, 'message': '中止信号を送信しました'})
    return jsonify({'success': False, 'error': '中止可能なタスクが見つかりません'})

@app.route('/api/progress')
def get_progress():
    """Server-Sent Eventsで進捗を配信"""
    session_id = session.get('task_id')
    if not session_id or session_id not in progress_queues:
        def error_stream():
            yield f"data: {json.dumps({'error': 'セッションが見つかりません'})}\n\n"
        response = Response(error_stream(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        return response
    
    def event_stream():
        try:
            while True:
                try:
                    # 進捗データを取得（5秒タイムアウト）
                    progress_data = progress_queues[session_id].get(timeout=5)
                    
                    # 進捗データの種類に応じて処理
                    if 'type' in progress_data:
                        event_data = progress_data
                    else:
                        # 進捗更新
                        event_data = {
                            'type': 'progress',
                            'explored_count': progress_data.get('explored_count', 0),
                            'current_moves': progress_data.get('current_moves', 0),
                            'estimated_remaining': progress_data.get('estimated_remaining', 0)
                        }
                    
                    yield f"data: {json.dumps(event_data)}\n\n"
                    
                    # 最終結果の場合は終了
                    if event_data.get('type') == 'final_result':
                        break
                        
                except queue.Empty:
                    # タイムアウト時はハートビートを送信
                    if session_id in progress_queues:
                        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                    else:
                        break
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # クリーンアップ
            if session_id in progress_queues:
                del progress_queues[session_id]
            if session_id in stop_flags:
                del stop_flags[session_id]
    
    response = Response(event_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response

@app.route('/api/get_step/<int:step>')
def get_step(step):
    """指定されたステップの状態を取得"""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかっていません'})
    
    solution_data = solution_cache[task_id]
    solution = solution_data['solution']
    
    if 0 <= step < len(solution):
        return jsonify({
            'success': True,
            'step': step,
            'board': solution[step]['board'],
            'move': solution[step]['move'],
            'total_steps': len(solution) - 1
        })
    else:
        return jsonify({'success': False, 'error': '無効なステップ番号です'})

@app.route('/api/next_step')
def next_step():
    """次のステップに進む"""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかっていません'})
    
    solution_data = solution_cache[task_id]
    current_step = solution_data['current_step']
    solution = solution_data['solution']
    
    if current_step < len(solution) - 1:
        current_step += 1
        solution_cache[task_id]['current_step'] = current_step
        
        return jsonify({
            'success': True,
            'step': current_step,
            'board': solution[current_step]['board'],
            'move': solution[current_step]['move'],
            'total_steps': len(solution) - 1,
            'is_final': current_step == len(solution) - 1
        })
    else:
        return jsonify({
            'success': False, 
            'error': '最終ステップに到達しています',
            'is_final': True
        })

@app.route('/api/prev_step')
def prev_step():
    """前のステップに戻る"""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかっていません'})
    
    solution_data = solution_cache[task_id]
    current_step = solution_data['current_step']
    solution = solution_data['solution']
    
    if current_step > 0:
        current_step -= 1
        solution_cache[task_id]['current_step'] = current_step
        
        return jsonify({
            'success': True,
            'step': current_step,
            'board': solution[current_step]['board'],
            'move': solution[current_step]['move'] if current_step > 0 else '初期状態',
            'total_steps': len(solution) - 1,
            'is_final': False
        })
    else:
        return jsonify({
            'success': False, 
            'error': '初期ステップです'
        })

@app.route('/api/reset')
def reset_puzzle():
    """パズルをリセット"""
    task_id = session.get('task_id')
    # 進捗キューとソリューションキャッシュをクリア
    if task_id:
        if task_id in progress_queues:
            del progress_queues[task_id]
        if task_id in solution_cache:
            del solution_cache[task_id]
        if task_id in stop_flags:
            del stop_flags[task_id]
    session.clear()
    return jsonify({'success': True})

@app.route('/api/validate_board', methods=['POST'])
def validate_board():
    """盤面の妥当性をチェック"""
    data = request.get_json()
    board = data.get('board')
    
    if not board or len(board) != 5 or any(len(row) != 4 for row in board):
        return jsonify({'success': False, 'error': '盤面のサイズが正しくありません'})
    
    # 必要なピースがすべて存在するかチェック
    pieces_count = {}
    for row in board:
        for cell in row:
            pieces_count[cell] = pieces_count.get(cell, 0) + 1
    
    # 箱入り娘(MP)が4マス存在するかチェック
    if pieces_count.get(1, 0) != 4:  # MP = 1
        return jsonify({'success': False, 'error': '箱入り娘(MP)が正しく配置されていません'})
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)