from flask import Flask, render_template, request, jsonify, session, Response, g
from hakoiri_puzzle import HakoiriPuzzle, HakoiriSolver, PIECE_PROPERTIES
import json
import signal
import threading
import time
import queue
import uuid

app = Flask(__name__)
app.secret_key = 'hakoiri-musume-puzzle-secret-key'

# グローバル進捗キューと解結果保存
progress_queues = {}
solution_cache = {}

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

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("アルゴリズムがタイムアウトしました")

def solve_with_timeout(solver_func, timeout_seconds=600):
    """タイムアウト付きでソルバーを実行"""