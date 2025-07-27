class HakoiriPuzzleUI {
    constructor() {
        this.board = Array(5).fill(null).map(() => Array(4).fill(0));
        this.selectedShape = 'empty';
        this.currentStep = 0;
        this.totalSteps = 0;
        this.solutionAvailable = false;
        this.solutionData = [];
        this.sessionId = Date.now().toString();
        
        // 進捗表示用
        this.progressEventSource = null;
        this.startTime = null;
        this.timerInterval = null;
        
        // ドラッグ&ドロップ用の状態
        this.draggedPieceId = null;
        this.draggedPieceOrigin = null;
        
        // 形状ベースの定義
        this.shapeDefinitions = {
            empty: { width: 1, height: 1, color: '#f8f9fa', maxCount: 999 },
            main: { width: 2, height: 2, color: '#FF6B6B', maxCount: 1 },
            horizontal: { width: 2, height: 1, color: '#4ECDC4', maxCount: 4 },
            vertical: { width: 1, height: 2, color: '#45B7D1', maxCount: 4 },
            square: { width: 1, height: 1, color: '#96CEB4', maxCount: 4 }
        };
        
        // 動的ID管理
        this.nextPieceIds = {
            main: 1,
            horizontal: 2,  // H1=2, H2=3, H3=4, H4=5
            vertical: 6,    // V1=6, V2=7, V3=8, V4=9
            square: 10      // S1=10, S2=11, S3=12, S4=13
        };
        
        // 既存のピースプロパティ（互換性のため）
        this.pieceProperties = {
            0: { width: 1, height: 1, name: '空', color: '#f8f9fa' },
            1: { width: 2, height: 2, name: 'MP', color: '#FF6B6B' },
            2: { width: 2, height: 1, name: 'H1', color: '#4ECDC4' },
            3: { width: 2, height: 1, name: 'H2', color: '#4ECDC4' },
            4: { width: 2, height: 1, name: 'H3', color: '#4ECDC4' },
            5: { width: 2, height: 1, name: 'H4', color: '#4ECDC4' },
            6: { width: 1, height: 2, name: 'V1', color: '#45B7D1' },
            7: { width: 1, height: 2, name: 'V2', color: '#45B7D1' },
            8: { width: 1, height: 2, name: 'V3', color: '#45B7D1' },
            9: { width: 1, height: 2, name: 'V4', color: '#45B7D1' },
            10: { width: 1, height: 1, name: 'S1', color: '#96CEB4' },
            11: { width: 1, height: 1, name: 'S2', color: '#96CEB4' },
            12: { width: 1, height: 1, name: 'S3', color: '#96CEB4' },
            13: { width: 1, height: 1, name: 'S4', color: '#96CEB4' }
        };
        
        this.init();
    }
    
    init() {
        this.createBoard();
        this.setupEventListeners();
        this.loadDefaultBoard();
    }
    
    createBoard() {
        const boardElement = document.getElementById('puzzle-board');
        boardElement.innerHTML = '';
        
        for (let row = 0; row < 5; row++) {
            for (let col = 0; col < 4; col++) {
                const cell = document.createElement('div');
                cell.className = 'board-cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                cell.addEventListener('click', (e) => this.handleCellClick(e));
                
                // ドラッグ&ドロップイベント
                cell.addEventListener('mousedown', (e) => this.handleMouseDown(e));
                cell.addEventListener('mouseover', (e) => this.handleMouseOver(e));
                cell.addEventListener('mouseup', (e) => this.handleMouseUp(e));
                
                boardElement.appendChild(cell);
            }
        }
        
        // 目標位置を示すマーカーを追加
        this.addGoalMarkers();
    }
    
    addGoalMarkers() {
        const boardElement = document.getElementById('puzzle-board');
        const goalRow = 3;
        const goalCols = [1, 2];
        
        goalCols.forEach(col => {
            for (let r = 0; r < 2; r++) {
                const cell = boardElement.children[(goalRow + r) * 4 + col];
                cell.classList.add('goal-cell');
            }
        });
    }
    
    setupEventListeners() {
        // ピース選択（形状ベース）
        document.querySelectorAll('.piece-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const shape = item.dataset.shape;
                
                // 最大数チェック
                if (shape !== 'empty' && this.getShapeCount(shape) >= this.shapeDefinitions[shape].maxCount) {
                    this.showMessage(`${item.dataset.name}の最大配置数に達しています`, 'warning');
                    return;
                }
                
                document.querySelectorAll('.piece-item').forEach(p => p.classList.remove('selected'));
                item.classList.add('selected');
                this.selectedShape = shape;
            });
        });
        
        // コントロールボタン
        document.getElementById('reset-board').addEventListener('click', () => this.resetBoard());
        document.getElementById('solve-puzzle').addEventListener('click', () => this.solvePuzzle());
        document.getElementById('stop-puzzle').addEventListener('click', () => this.stopSolving());
        
        // ステップコントロール（メイン）
        document.getElementById('next-step-main').addEventListener('click', () => this.nextStep());
        document.getElementById('prev-step-main').addEventListener('click', () => this.prevStep());
        
        // デフォルトで空が選択されている（HTMLで設定済み）
    }
    
    loadDefaultBoard() {
        // デフォルトの盤面を設定（確実に解ける標準配置・約30手）
        this.board = [
            [12, 4, 4, 13],  // S3, H3, H3, S4
            [6, 1, 1, 7],    // V1, MP, MP, V2
            [6, 1, 1, 7],    // V1, MP, MP, V2
            [10, 2, 2, 11],  // S1, H1, H1, S2
            [0, 3, 3, 0]     // EM, H2, H2, EM
        ];
        this.renderBoard();
    }
    
    handleCellClick(event) {
        if (this.solutionAvailable) {
            this.showMessage('解の表示中は盤面を編集できません', 'warning');
            return;
        }
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        
        if (this.selectedShape === 'empty') {
            // 空のセルに設定（マルチセルピースの場合は全体を消去）
            this.clearPieceAt(row, col);
        } else {
            // ピースを配置
            this.placeShapePiece(row, col, this.selectedShape);
        }
        
        this.renderBoard();
    }
    
    handleMouseDown(event) {
        if (this.solutionAvailable) return; // 解の表示中はドラッグ無効
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        const pieceId = this.board[row][col];
        
        if (pieceId === 0) return; // 空のセルはドラッグできない
        
        // ドラッグ開始
        this.draggedPieceId = pieceId;
        this.draggedPieceOrigin = { row, col };
        
        // ドラッグ中の視覚的フィードバック
        this.highlightDraggedPiece(pieceId, true);
        
        // マウスカーソルを変更
        document.body.style.cursor = 'grabbing';
        
        // ドラッグ中はクリックイベントを無効化
        event.preventDefault();
    }
    
    handleMouseOver(event) {
        if (!this.draggedPieceId) return;
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        
        // ドロップ可能な位置かチェック
        if (this.canDropPieceAt(this.draggedPieceId, row, col)) {
            event.target.classList.add('drop-target');
            this.highlightDropZone(this.draggedPieceId, row, col, true);
        } else {
            this.clearDropHighlights();
        }
    }
    
    handleMouseUp(event) {
        if (!this.draggedPieceId) return;
        
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);
        
        // ドロップ実行
        if (this.canDropPieceAt(this.draggedPieceId, row, col)) {
            this.movePiece(this.draggedPieceId, this.draggedPieceOrigin, { row, col });
            this.renderBoard();
        }
        
        // ドラッグ状態をリセット
        this.clearDragState();
    }
    
    clearDragState() {
        this.highlightDraggedPiece(this.draggedPieceId, false);
        this.clearDropHighlights();
        this.draggedPieceId = null;
        this.draggedPieceOrigin = null;
        document.body.style.cursor = 'default';
    }
    
    highlightDraggedPiece(pieceId, highlight) {
        if (!pieceId) return;
        
        const cells = document.querySelectorAll(`[data-piece-id="${pieceId}"]`);
        cells.forEach(cell => {
            if (highlight) {
                cell.classList.add('dragging');
            } else {
                cell.classList.remove('dragging');
            }
        });
    }
    
    highlightDropZone(pieceId, row, col, highlight) {
        const properties = this.pieceProperties[pieceId];
        if (!properties) return;
        
        for (let r = 0; r < properties.height; r++) {
            for (let c = 0; c < properties.width; c++) {
                const targetRow = row + r;
                const targetCol = col + c;
                if (targetRow < 5 && targetCol < 4) {
                    const cell = document.querySelector(`[data-row="${targetRow}"][data-col="${targetCol}"]`);
                    if (cell) {
                        if (highlight) {
                            cell.classList.add('drop-zone');
                        } else {
                            cell.classList.remove('drop-zone');
                        }
                    }
                }
            }
        }
    }
    
    clearDropHighlights() {
        document.querySelectorAll('.drop-target').forEach(cell => {
            cell.classList.remove('drop-target');
        });
        document.querySelectorAll('.drop-zone').forEach(cell => {
            cell.classList.remove('drop-zone');
        });
    }
    
    canDropPieceAt(pieceId, row, col) {
        const properties = this.pieceProperties[pieceId];
        if (!properties) return false;
        
        // 境界チェック
        if (row + properties.height > 5 || col + properties.width > 4) {
            return false;
        }
        
        // 配置可能性チェック
        for (let r = 0; r < properties.height; r++) {
            for (let c = 0; c < properties.width; c++) {
                const targetRow = row + r;
                const targetCol = col + c;
                const currentPieceId = this.board[targetRow][targetCol];
                
                // 空きセルまたは移動中のピース自身の場合のみOK
                if (currentPieceId !== 0 && currentPieceId !== pieceId) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    movePiece(pieceId, fromPos, toPos) {
        const properties = this.pieceProperties[pieceId];
        if (!properties) return;
        
        // 元の位置をクリア
        for (let r = 0; r < 5; r++) {
            for (let c = 0; c < 4; c++) {
                if (this.board[r][c] === pieceId) {
                    this.board[r][c] = 0;
                }
            }
        }
        
        // 新しい位置に配置
        for (let r = 0; r < properties.height; r++) {
            for (let c = 0; c < properties.width; c++) {
                this.board[toPos.row + r][toPos.col + c] = pieceId;
            }
        }
    }
    
    clearPieceAt(row, col) {
        const pieceId = this.board[row][col];
        if (pieceId === 0) return;
        
        // 同じピースIDのセルをすべてクリア
        for (let r = 0; r < 5; r++) {
            for (let c = 0; c < 4; c++) {
                if (this.board[r][c] === pieceId) {
                    this.board[r][c] = 0;
                }
            }
        }
    }
    
    placeShapePiece(row, col, shape) {
        const shapeData = this.shapeDefinitions[shape];
        if (!shapeData) return;
        
        // 配置可能かチェック
        if (row + shapeData.height > 5 || col + shapeData.width > 4) {
            this.showMessage('範囲外に配置することはできません', 'warning');
            return;
        }
        
        // 重複チェック
        for (let r = 0; r < shapeData.height; r++) {
            for (let c = 0; c < shapeData.width; c++) {
                if (this.board[row + r][col + c] !== 0) {
                    this.showMessage('他のピースと重複しています', 'warning');
                    return;
                }
            }
        }
        
        // 最大数チェック
        if (this.getShapeCount(shape) >= shapeData.maxCount) {
            this.showMessage(`${shape}の最大配置数に達しています`, 'warning');
            return;
        }
        
        // 新しいピースIDを取得
        const pieceId = this.getNextPieceId(shape);
        
        // 配置
        for (let r = 0; r < shapeData.height; r++) {
            for (let c = 0; c < shapeData.width; c++) {
                this.board[row + r][col + c] = pieceId;
            }
        }
    }
    
    getNextPieceId(shape) {
        const baseId = this.nextPieceIds[shape];
        const maxCount = this.shapeDefinitions[shape].maxCount;
        
        for (let i = 0; i < maxCount; i++) {
            const checkId = baseId + i;
            if (!this.isPieceIdUsed(checkId)) {
                return checkId;
            }
        }
        
        return baseId; // フォールバック
    }
    
    isPieceIdUsed(pieceId) {
        for (let r = 0; r < 5; r++) {
            for (let c = 0; c < 4; c++) {
                if (this.board[r][c] === pieceId) {
                    return true;
                }
            }
        }
        return false;
    }
    
    getShapeCount(shape) {
        const baseId = this.nextPieceIds[shape];
        const maxCount = this.shapeDefinitions[shape].maxCount;
        let count = 0;
        
        for (let i = 0; i < maxCount; i++) {
            const checkId = baseId + i;
            if (this.isPieceIdUsed(checkId)) {
                count++;
            }
        }
        
        return count;
    }
    
    renderBoard() {
        const cells = document.querySelectorAll('.board-cell');
        
        cells.forEach((cell, index) => {
            const row = Math.floor(index / 4);
            const col = index % 4;
            const pieceId = this.board[row][col];
            
            // ピースIDをセット
            cell.dataset.pieceId = pieceId;
            
            // ピース名を表示
            if (pieceId === 0) {
                cell.textContent = '';
            } else if (this.pieceProperties[pieceId]) {
                cell.textContent = this.pieceProperties[pieceId].name;
            } else {
                cell.textContent = pieceId;
            }
        });
    }
    
    resetBoard() {
        if (this.solutionAvailable) {
            this.showMessage('解の表示中は盤面をリセットできません', 'warning');
            return;
        }
        
        this.board = Array(5).fill(null).map(() => Array(4).fill(0));
        this.renderBoard();
        
        // ピース選択を「空」に戻す
        document.querySelectorAll('.piece-item').forEach(item => item.classList.remove('selected'));
        document.querySelector('[data-shape="empty"]').classList.add('selected');
        this.selectedShape = 'empty';
        
        this.showMessage('盤面をリセットしました', 'info');
    }
    
    async solvePuzzle() {
        this.startProgressIndicator();
        
        try {
            // 盤面の初期化
            const initResponse = await fetch('/api/initialize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    board: this.board,
                    session_id: this.sessionId
                })
            });
            const initData = await initResponse.json();
            
            if (!initData.success) {
                this.stopProgressIndicator();
                this.showMessage('初期化に失敗しました: ' + initData.error, 'error');
                return;
            }
            
            // パズルを解く（バックグラウンド処理開始）
            const solveResponse = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const solveData = await solveResponse.json();
            
            if (solveData.success) {
                // リアルタイム進捗表示開始
                this.startRealTimeProgress();
            } else {
                this.stopProgressIndicator();
                this.showMessage('解決開始に失敗しました: ' + solveData.error, 'error');
            }
            
        } catch (error) {
            this.stopProgressIndicator();
            this.showMessage('エラーが発生しました: ' + error.message, 'error');
        }
    }
    
    async stopSolving() {
        try {
            const response = await fetch('/api/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.sessionId })
            });
            
            if (response.ok) {
                this.showMessage('探索を中止しました', 'info');
            }
        } catch (error) {
            console.error('Stop request failed:', error);
        }
        
        this.stopProgressIndicator();
    }
    
    startProgressIndicator() {
        this.startTime = Date.now();
        this.startTimer();
        
        // ボタンの表示を切り替え
        document.getElementById('solve-puzzle').style.display = 'none';
        document.getElementById('stop-puzzle').style.display = 'inline-block';
        
        // 統計値をリセット
        document.getElementById('explored-count').textContent = '0';
        document.getElementById('current-moves').textContent = '0';
        document.getElementById('estimated-remaining').textContent = '-';
    }
    
    stopProgressIndicator() {
        this.stopTimer();
        
        // ボタンの表示を元に戻す
        document.getElementById('solve-puzzle').style.display = 'inline-block';
        document.getElementById('stop-puzzle').style.display = 'none';
        
        // 進捗受信を停止
        if (this.progressEventSource) {
            this.progressEventSource.close();
            this.progressEventSource = null;
        }
    }
    
    startTimer() {
        this.timerInterval = setInterval(() => {
            if (this.startTime) {
                const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
                document.getElementById('elapsed-time').textContent = `${elapsed}秒`;
            }
        }, 1000);
    }
    
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    startRealTimeProgress() {
        if (this.progressEventSource) {
            this.progressEventSource.close();
        }
        
        // Server-Sent Eventsで進捗を受信
        this.progressEventSource = new EventSource('/api/progress');
        
        this.progressEventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleProgressUpdate(data);
            } catch (error) {
                console.error('進捗データのパースエラー:', error);
            }
        };
        
        this.progressEventSource.onerror = (error) => {
            console.error('進捗受信エラー:', error);
            this.progressEventSource.close();
            this.progressEventSource = null;
        };
    }
    
    handleProgressUpdate(data) {
        if (data.type === 'progress') {
            // 進捗更新
            this.updateRealTimeProgress(data);
        } else if (data.type === 'final_result') {
            // 最終結果
            this.handleFinalResult(data);
        } else if (data.type === 'heartbeat') {
            // ハートビート（何もしない）
        } else if (data.error) {
            this.stopProgressIndicator();
            this.showMessage('進捗取得エラー: ' + data.error, 'error');
        }
    }
    
    updateRealTimeProgress(data) {
        // 探索件数を更新
        const exploredCountElement = document.getElementById('explored-count');
        if (exploredCountElement) {
            const countText = `${data.explored_count.toLocaleString()}`;
            if (exploredCountElement.textContent !== countText) {
                exploredCountElement.classList.add('updating');
                exploredCountElement.textContent = countText;
                setTimeout(() => exploredCountElement.classList.remove('updating'), 300);
            }
        }
        
        // 現在手数を更新
        const currentMovesElement = document.getElementById('current-moves');
        if (currentMovesElement) {
            const movesText = `${data.current_moves}`;
            if (currentMovesElement.textContent !== movesText) {
                currentMovesElement.classList.add('updating');
                currentMovesElement.textContent = movesText;
                setTimeout(() => currentMovesElement.classList.remove('updating'), 300);
            }
        }
        
        // 推定残り手数を更新
        const estimatedRemainingElement = document.getElementById('estimated-remaining');
        if (estimatedRemainingElement) {
            const remainingText = `${data.estimated_remaining}`;
            if (estimatedRemainingElement.textContent !== remainingText) {
                estimatedRemainingElement.classList.add('updating');
                estimatedRemainingElement.textContent = remainingText;
                setTimeout(() => estimatedRemainingElement.classList.remove('updating'), 300);
            }
        }
    }
    
    handleFinalResult(data) {
        this.stopProgressIndicator();
        
        if (data.solved) {
            // 解法成功
            this.solutionData = data.solution;
            this.totalSteps = data.total_steps;
            this.currentStep = 0;
            this.solutionAvailable = true;
            
            this.showMessage(`解法が見つかりました！(${data.total_steps - 1}手)`, 'success');
            this.showStepControls();
            this.displayStep(0);
        } else {
            // 解法失敗
            this.showMessage(data.message || '解が見つかりませんでした', 'error');
        }
    }
    
    showStepControls() {
        const stepControls = document.getElementById('step-controls');
        stepControls.style.display = 'flex';
        this.updateStepDisplay();
    }
    
    hideStepControls() {
        const stepControls = document.getElementById('step-controls');
        stepControls.style.display = 'none';
    }
    
    nextStep() {
        if (this.currentStep < this.totalSteps - 1) {
            this.currentStep++;
            this.displayStep(this.currentStep);
            this.updateStepDisplay();
        }
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.displayStep(this.currentStep);
            this.updateStepDisplay();
        }
    }
    
    displayStep(step) {
        if (this.solutionData && step < this.solutionData.length) {
            this.board = this.solutionData[step];
            this.renderBoard();
        }
    }
    
    updateStepDisplay() {
        const stepDisplay = document.getElementById('step-display');
        stepDisplay.textContent = `${this.currentStep + 1} / ${this.totalSteps}`;
        
        // ボタンの有効/無効を制御
        document.getElementById('prev-step-main').disabled = this.currentStep === 0;
        document.getElementById('next-step-main').disabled = this.currentStep === this.totalSteps - 1;
    }
    
    showMessage(message, type = 'info', autoHide = true) {
        const messageArea = document.getElementById('message-area');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        
        messageArea.appendChild(messageElement);
        
        // クリックで閉じる
        messageElement.addEventListener('click', () => {
            messageElement.remove();
        });
        
        // 自動で閉じる
        if (autoHide) {
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 5000);
        }
    }
}

// アプリケーション開始
document.addEventListener('DOMContentLoaded', () => {
    new HakoiriPuzzleUI();
});