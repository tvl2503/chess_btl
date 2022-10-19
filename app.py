from distutils.log import error
import chess
import chess.svg
import chess.polyglot
import traceback
import chess.pgn
import chess.engine
from flask import Flask, Response, jsonify, render_template, request, url_for,redirect, session,json
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import json
from flask_cors import CORS
from flask_socketio import SocketIO
ls = ''
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'volinh01'
app.config['MYSQL_DB'] = 'chess'
app.config['UPLOAD_FOLDER']=os.path.join('static','pics')

app.config['CORS_HEADERS'] = 'Content-Type'
mysql = MySQL(app)
pawntable = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0]

knightstable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

bishopstable = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]

rookstable = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0]

queenstable = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]

kingstable = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]


def evaluate_board():
    if board.is_checkmate():
        if board.turn:
            return -9999
        else:
            return 9999
    if board.is_stalemate():
        return 0
    if board.is_insufficient_material():
        return 0

    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    material = 100 * (wp - bp) + 320 * (wn - bn) + 330 * (wb - bb) + 500 * (wr - br) + 900 * (wq - bq)

    pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
    pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)]
                           for i in board.pieces(chess.PAWN, chess.BLACK)])
    knightsq = sum([knightstable[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.KNIGHT, chess.BLACK)])
    bishopsq = sum([bishopstable[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
    bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.BISHOP, chess.BLACK)])
    rooksq = sum([rookstable[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
    rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.ROOK, chess.BLACK)])
    queensq = sum([queenstable[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
    queensq = queensq + sum([-queenstable[chess.square_mirror(i)]
                             for i in board.pieces(chess.QUEEN, chess.BLACK)])
    kingsq = sum([kingstable[i] for i in board.pieces(chess.KING, chess.WHITE)])
    kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.KING, chess.BLACK)])

    eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
    if board.turn:
        return eval
    else:
        return -eval


def alphabeta(alpha, beta, depthleft):
    bestscore = -9999
    if (depthleft == 0):
        return quiesce(alpha, beta)
    for move in board.legal_moves:
        board.push(move)
        score = -alphabeta(-beta, -alpha, depthleft - 1)
        board.pop()
        if (score >= beta):
            return score
        if (score > bestscore):
            bestscore = score
        if (score > alpha):
            alpha = score
    return bestscore


def quiesce(alpha, beta):
    stand_pat = evaluate_board()
    if (stand_pat >= beta):
        return beta
    if (alpha < stand_pat):
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiesce(-beta, -alpha)
            board.pop()

            if (score >= beta):
                return beta
            if (score > alpha):
                alpha = score
    return alpha


def selectmove(depth):
    bestMove = chess.Move.null()
    bestValue = -99999
    alpha = -100000
    beta = 100000
    for move in board.legal_moves:
        board.push(move)
        boardValue = -alphabeta(-beta, -alpha, depth - 1)
        if boardValue > bestValue:
            bestValue = boardValue
            bestMove = move
        if (boardValue > alpha):
            alpha = boardValue
        board.pop()
    return bestMove



def stockfish():
    engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")
    move = engine.play(board, chess.engine.Limit(time=0.1))

    board.push(move.move)


def stockfish2():
    engine = chess.engine.SimpleEngine.popen_uci("stockfish.exe")
    move = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(move.move)

    return board.fen()

def check_acc(username, email):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM player WHERE username = %s AND email = %s' , (username,email))
    account = cursor.fetchone()
    if not account:
        return None
    else:
        return account
# Front Page of the Flask Web Page
@app.route("/")
def main():

  
    global count, board
    print(board.move_stack)

    if count == 1:
        count += 1
    return render_template("index.html", src = "/board.svg")
    

@app.route("/board.svg/")
def board():
    return Response(chess.svg.board(board=board, size=700), mimetype='image/svg+xml')

@app.route("/api/login", methods = ['POST'])
def login():
        msg = ''
        try:
            email = request.args.get('email')
            password = request.args.get('password')
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM player WHERE email = % s AND password = % s', (email, password ))
            acc = cursor.fetchone()
            print(acc)
            if acc:
                acc.pop("password")
                msg = 'Logged in successfully !'
                return jsonify({"acc" :(json.dumps(acc)), "msg" : msg, "code" : 200})
            else: 
                msg = 'Incorrect username / password !'
                return jsonify({"code" : 400, "msg" : msg})
        except Exception as e :
            print("ee",e)
            msg = 'error '
            return jsonify("Lỗi")
   
@app.route('/api/register',methods = ['GET', 'POST'])
def register():
    msg = ''
    try: 
        username = request.args.get('username')
        password = request.args.get('password')
        fullname = request.args.get('fullname')
        email = request.args.get('email')
        acc = check_acc(username, email)
        if not acc: 
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO player ( username, password, fullname, email) VALUES (%s,%s,%s,%s)', (username,password,fullname,email))
            mysql.connection.commit()
            print("da den day")
            return jsonify({"msg" : "Đăng ký thành công"})
        else:
            msg = 'Tài khoản đã tồn tại'
            return jsonify({msg})
    except  :
            msg = 'error '
            return jsonify({msg})
    


@app.route("/api/move", methods = ['POST'] )
def move():
    try:

        move = request.args.get("move")
        board.push_san(move)
        stockfish()

        history = []
        for i in range(len(board.move_stack)):
            history.append(str(board.move_stack[i]))
        return jsonify({"fen": str(board.fen()), "history" : history})
    except :
        return jsonify("error", 404)
    # return main()

@app.route("/engine/", methods=['POST'])
def engine():
    try:
        stockfish()

    except Exception:
        traceback.print_exc()
    return main()

@app.route("/engine2/")
def engine2():
    try:
        move = stockfish2()
        s = str(move)
        return jsonify({"moved" : s})
    except Exception:
        traceback.print_exc()
        return jsonify({"move"})

# Alpha Beta Move
@app.route('/AlphaBeta/',methods=['POST'])
def alpha_beta():
    try:
        move = selectmove(3)
        board.push_san(str(move))
    except Exception:
        traceback.print_exc()
    return main() 


# New Game
@app.route("/api/game/", methods=['GET'])
def game():
    board.reset()
    return jsonify({"fen": str(board.fen())})
@socketio.on('message') 
def handlemsg():
    socketio.send(jsonify({"fen": str(board.fen())}))
@app.route("/rank/")
def rank():
    board.reset()
    return render_template("rank.html")


# Undo
@app.route("/api/undo/", methods=['POST'])
def undo():
    try:
        board.pop();
        board.pop();

        history = []
        for i in range(len(board.move_stack)):
            history.append(str(board.move_stack[i]))
        return jsonify({"fen": str(board.fen()), "history" : history})
    except Exception:
        traceback.print_exc()
    return main()



# Main Function
if __name__ == '__main__':
    count = 1
    board = chess.Board()
    app.run(debug = True)
