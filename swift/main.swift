import Foundation

let lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
var nodes = 0

func winner(_ board: [Character]) -> Character? {
    for line in lines {
        let (a, b, c) = (line[0], line[1], line[2])
        if board[a] != "-" && board[a] == board[b] && board[b] == board[c] { return board[a] }
    }
    return nil
}

func minimax(_ board: inout [Character], current: Character, ai: Character, depth: Int, alpha: Int, beta: Int) -> Int {
    nodes += 1
    if let win = winner(board) {
        return win == ai ? 10 - depth : depth - 10
    }
    if !board.contains("-") { return 0 }

    let maximizing = current == ai
    var best = maximizing ? -100 : 100
    var localAlpha = alpha
    var localBeta = beta

    for i in board.indices where board[i] == "-" {
        board[i] = current
        let score = minimax(&board, current: current == "X" ? "O" : "X", ai: ai, depth: depth + 1, alpha: localAlpha, beta: localBeta)
        board[i] = "-"
        if maximizing {
            best = max(best, score)
            localAlpha = max(localAlpha, best)
        } else {
            best = min(best, score)
            localBeta = min(localBeta, best)
        }
        if localBeta <= localAlpha { break }
    }
    return best
}

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data("error: \(message)\n".utf8))
    exit(2)
}

let args = CommandLine.arguments
let boardText = (args.count > 1 ? args[1] : "XX-OO----").uppercased()
let playerText = (args.count > 2 ? args[2] : "X").uppercased()
let valid: Set<Character> = ["X", "O", "-"]
var board = Array(boardText)
if board.count != 9 || board.contains(where: { !valid.contains($0) }) { fail("invalid board") }
if playerText != "X" && playerText != "O" { fail("player must be X or O") }
let ai = Character(playerText)
if winner(board) != nil || !board.contains("-") { fail("board must be non-terminal") }

var bestMove = -1
var bestScore = -100
nodes = 0
for i in board.indices where board[i] == "-" {
    board[i] = ai
    let score = minimax(&board, current: ai == "X" ? "O" : "X", ai: ai, depth: 1, alpha: -100, beta: 100)
    board[i] = "-"
    if score > bestScore {
        bestScore = score
        bestMove = i
    }
}

print("{\"language\":\"swift\",\"move\":\(bestMove),\"score\":\(bestScore),\"nodes\":\(nodes)}")
