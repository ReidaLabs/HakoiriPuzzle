import os
from flask import Flask, render_template, request, jsonify, session, Response
from hakoiri_puzzle import HakoiriPuzzle, HakoiriSolver, PIECE_PROPERTIES
import json
import threading
import time
import queue
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')

<<<<<<< HEAD
# グローバル進捗キューと解結果保存
=======
# グローバル進捗キューと解結果保孁E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
progress_queues = {}
solution_cache = {}
stop_flags = {}  # 探索中止フラグ

@app.route('/')
def index():
<<<<<<< HEAD
    """メインページを表示"""
=======
    """メインペ�Eジを表示"""
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize_puzzle():
<<<<<<< HEAD
    """パズルを初期化"""
=======
    """パズルを�E期化"""
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    data = request.get_json()
    board = data.get('board')
    
    puzzle = HakoiriPuzzle()
    if board:
        puzzle.set_initial_board(board)
    
<<<<<<< HEAD
    # セッションにパズルの初期状態を保存
=======
    # セチE��ョンにパズルの初期状態を保孁E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    session['initial_board'] = puzzle.initial_board
    session['current_step'] = 0
    session['solution'] = None
    
    return jsonify({
        'success': True,
        'board': puzzle.initial_board,
        'piece_properties': PIECE_PROPERTIES
    })

def create_progress_callback(session_id):
<<<<<<< HEAD
    """進捗コールバック関数を作成"""
=======
    """進捗コールバック関数を作�E"""
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    def progress_callback(info):
        if session_id in progress_queues:
            try:
                progress_queues[session_id].put_nowait(info)
            except queue.Full:
<<<<<<< HEAD
                # キューが満杯の場合は古いデータを1つ削除してから追加
=======
                # キューが満杯の場合�E古ぁE��ータめEつ削除してから追加
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
                try:
                    progress_queues[session_id].get_nowait()
                    progress_queues[session_id].put_nowait(info)
                except queue.Empty:
                    pass
    return progress_callback

@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
<<<<<<< HEAD
    """パズルを解く（リアルタイム進捗表示付き）"""
    if 'initial_board' not in session:
        return jsonify({'success': False, 'error': 'パズルが初期化されていません'})
    
    # ユニークなセッションIDを生成
=======
    """パズルを解く（リアルタイム進捗表示付き�E�E""
    if 'initial_board' not in session:
        return jsonify({'success': False, 'error': 'パズルが�E期化されてぁE��せん'})
    
    # ユニ�EクなセチE��ョンIDを生戁E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    session_id = str(uuid.uuid4())
    session['task_id'] = session_id
    progress_queues[session_id] = queue.Queue(maxsize=50)
    stop_flags[session_id] = False
    
<<<<<<< HEAD
    # 初期盤面をコピー（バックグラウンドスレッド用）
=======
    # 初期盤面をコピ�E�E�バチE��グラウンドスレチE��用�E�E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    initial_board = [row[:] for row in session['initial_board']]
    
    puzzle = HakoiriPuzzle()
    puzzle.set_initial_board(initial_board)
    
    solver = HakoiriSolver(puzzle)
    solver.set_progress_callback(create_progress_callback(session_id))
    
<<<<<<< HEAD
    # 中止フラグチェック関数をソルバーに設定
=======
    # 中止フラグチェチE��関数をソルバ�Eに設宁E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    solver.set_stop_flag_function(lambda: stop_flags.get(session_id, False))
    
    def solve_in_background():
        try:
            solution = solver.solve_astar()
            
            if solution:
<<<<<<< HEAD
                # 解をグローバルキャッシュに保存
=======
                # 解をグローバルキャチE��ュに保孁E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
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
                
<<<<<<< HEAD
            # 安全にキューに追加
=======
            # 安�Eにキューに追加
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
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
<<<<<<< HEAD
            yield f"data: {json.dumps({'error': 'セッションが見つかりません'})}\n\n"
=======
            yield f"data: {json.dumps({'error': 'セチE��ョンが見つかりません'})}\n\n"
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
        response = Response(error_stream(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        return response
    
    def event_stream():
        try:
            while True:
                try:
<<<<<<< HEAD
                    # 進捗データを取得（5秒タイムアウト）
                    progress_data = progress_queues[session_id].get(timeout=5)
                    
                    # 進捗データの種類に応じて処理
=======
                    # 進捗データを取得！E秒タイムアウト！E
                    progress_data = progress_queues[session_id].get(timeout=5)
                    
                    # 進捗データの種類に応じて処琁E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
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
                    
<<<<<<< HEAD
                    # 最終結果の場合は終了
=======
                    # 最終結果の場合�E終亁E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
                    if event_data.get('type') == 'final_result':
                        break
                        
                except queue.Empty:
<<<<<<< HEAD
                    # タイムアウト時はハートビートを送信
=======
                    # タイムアウト時はハ�Eトビートを送信
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
                    if session_id in progress_queues:
                        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                    else:
                        break
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
<<<<<<< HEAD
            # クリーンアップ
=======
            # クリーンアチE�E
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
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
<<<<<<< HEAD
    """指定されたステップの状態を取得"""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかっていません'})
=======
    """持E��されたスチE��プ�E状態を取征E""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかってぁE��せん'})
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    
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
<<<<<<< HEAD
        return jsonify({'success': False, 'error': '無効なステップ番号です'})

@app.route('/api/next_step')
def next_step():
    """次のステップに進む"""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかっていません'})
=======
        return jsonify({'success': False, 'error': '無効なスチE��プ番号でぁE})

@app.route('/api/next_step')
def next_step():
    """次のスチE��プに進む"""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかってぁE��せん'})
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    
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
<<<<<<< HEAD
            'error': '最終ステップに到達しています',
=======
            'error': '最終スチE��プに到達してぁE��ぁE,
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
            'is_final': True
        })

@app.route('/api/prev_step')
def prev_step():
<<<<<<< HEAD
    """前のステップに戻る"""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかっていません'})
=======
    """前�EスチE��プに戻めE""
    task_id = session.get('task_id')
    if not task_id or task_id not in solution_cache:
        return jsonify({'success': False, 'error': '解が見つかってぁE��せん'})
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    
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
<<<<<<< HEAD
            'move': solution[current_step]['move'] if current_step > 0 else '初期状態',
=======
            'move': solution[current_step]['move'] if current_step > 0 else '初期状慁E,
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
            'total_steps': len(solution) - 1,
            'is_final': False
        })
    else:
        return jsonify({
            'success': False, 
<<<<<<< HEAD
            'error': '初期ステップです'
=======
            'error': '初期スチE��プでぁE
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
        })

@app.route('/api/reset')
def reset_puzzle():
<<<<<<< HEAD
    """パズルをリセット"""
    task_id = session.get('task_id')
    # 進捗キューとソリューションキャッシュをクリア
=======
    """パズルをリセチE��"""
    task_id = session.get('task_id')
    # 進捗キューとソリューションキャチE��ュをクリア
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
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
<<<<<<< HEAD
    """盤面の妥当性をチェック"""
=======
    """盤面の妥当性をチェチE��"""
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    data = request.get_json()
    board = data.get('board')
    
    if not board or len(board) != 5 or any(len(row) != 4 for row in board):
        return jsonify({'success': False, 'error': '盤面のサイズが正しくありません'})
    
<<<<<<< HEAD
    # 必要なピースがすべて存在するかチェック
=======
    # 忁E��なピ�Eスがすべて存在するかチェチE��
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    pieces_count = {}
    for row in board:
        for cell in row:
            pieces_count[cell] = pieces_count.get(cell, 0) + 1
    
<<<<<<< HEAD
    # 箱入り娘(MP)が4マス存在するかチェック
    if pieces_count.get(1, 0) != 4:  # MP = 1
        return jsonify({'success': False, 'error': '箱入り娘(MP)が正しく配置されていません'})
=======
    # 箱入り威EMP)ぁEマス存在するかチェチE��
    if pieces_count.get(1, 0) != 4:  # MP = 1
        return jsonify({'success': False, 'error': '箱入り威EMP)が正しく配置されてぁE��せん'})
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
    
    return jsonify({'success': True})

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True, port=5000)
=======
    app.run(debug=True, port=5000)
>>>>>>> 9614f998bb362e5174d410cd7269833c1dede4bd
