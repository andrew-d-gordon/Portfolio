import java.util.Random;

public class SnakeLadders {
	//Work in progress, mostly practice for subclasses
	public static void main(String[] args) {
		Player[] players = new Player[3];
		players[0] = new Player("abc");
		players[1] = new Player("def");
		players[2] = new Player("ghi");
		Board myBoard = new Board(5);
		myBoard.setCellToLadder(7, 17);
		myBoard.setCellToLadder(5, 14);
		myBoard.setCellToSnake(19, 8);
		myBoard.setCellToSnake(16, 4);
		Game game = new Game(myBoard, players);
		Player p = new Player("jkl");
		game.addPlayer(p);
		boolean b = false;
		Random random = new Random();
		int n;
		while (!b) {
			n = random.nextInt(6) + 1;
			b = game.play(n);
		}
		System.out.println(game.currentPlayer().getName());
	}

}

class Game {
	private Board board;
	private Player[] players;
	private int moveCount;

	// creates game with the board and players passed to constructor
	public Game(Board board, Player[] players) {
		this.board = board;
		this.players = players;
		for (int i = 0; i < players.length; i++)
			players[i].setPosition(0);
	}

	// creates 10 by 10 board and the players which are passed to it
	public Game(Player[] players) {
		this.board = new Board(10);
		this.players = players;
	}

	// specifies current player
	public Player currentPlayer() {
		int playerNumber = this.moveCount % players.length;
		return players[playerNumber];
	}

	// adds a player to list of players and player will be placed in first cell
	public void addPlayer(Player p) {
		Player[] newPlayers = new Player[players.length + 1];
		for (int i = 0; i < players.length; i++) {
			newPlayers[i] = players[i];
		}
		newPlayers[newPlayers.length - 1] = p;
		players = newPlayers;
		players[players.length - 1].setPosition(0);
	}

	// determines whether current player has reached last cell.
	public boolean winner() {
		if ((this.currentPlayer()).getPosition() == this.board.board.length)
			return true;
		else
			return false;
	}

	// moves current player 'n' cells forward
	public void movePlayer(int n) {
		System.out.println(this.currentPlayer().getPosition()); // replace most n's with currentPosition
		// System.out.println(this.board.getCells());
		if (this.board.board[n].isOccupied())
			; // checks for isoccupied
		this.currentPlayer().setPosition(0);
		this.currentPlayer().setPosition(n);// will go here on the first turn, and set the first n space on board to
											// occupied
		this.board.board[n].setOccupied(true);
		System.out.println(this.currentPlayer().getPosition());
		if (this.board.board[this.currentPlayer().getPosition()].getLadder() != null)
			this.currentPlayer().setPosition(this.board.board[n].getLadder().getTop());
		if (this.board.board[this.currentPlayer().getPosition()].getSnake() != null)
			this.currentPlayer().setPosition(this.board.board[n].getSnake().getTail());
		System.out.println(this.currentPlayer().getPosition());
	}

	/*
	 * This is main method in your game, moves current player to correct cell and
	 * also checks whether game is finished or not. if found a winner, returns true,
	 * otherwise returns false.
	 */
	public boolean play(int moveCount) {
		this.moveCount = moveCount;
		movePlayer(this.moveCount);
		if (this.currentPlayer().getPosition() == this.board.board.length - 1)
			return true;
		else
			return false;
	}

	// returns board of the game
	public Board getBoard() {
		return this.board;
	}
}

class Player {
	private String name;
	private int position;

	// constructor of player class
	public Player(String name) {
		this.name = name;
	}

	// moves player to specified position
	public void setPosition(int position) {
		this.position = position;
	}

	// returns position of the player
	public int getPosition() {
		return this.position;
	}

	// returns player's name
	public String getName() {
		return this.name;
	}

	// returns "Name @ cell-number" e.g. narges @ 12
	public String toString() {
		return name + " @ " + position;
	}
}

class Cell {
	private int number;
	private Ladder ladder;
	private Snake snake;
	private boolean occupied = false;

	// creates a cell and assigns its number
	public Cell(int number) {
		this.number = number;
	}

	// fills or releases the cell
	public void setOccupied(boolean occupied) {
		this.occupied = occupied;
	}

	// determines whether this cell is occupied
	public boolean isOccupied() {
		if (occupied == true)
			return true;
		else
			return false;
	}

	/*
	 * returns the ladder which is in the current cell. Returns null if no ladder
	 * with start in cell
	 */
	public Ladder getLadder() {
		if (ladder != null)
			return ladder;
		else
			return null;
	}

	/*
	 * returns snake which is in current cell. Returns null if no snake with head in
	 * this cell.
	 */
	public Snake getSnake() {
		if (snake != null)
			return snake;
		else
			return null;
	}

	// sets a ladder with start in the current cell
	public void setLadder(Ladder ladder) {
		System.out.println("set ladder");
		this.ladder = ladder;
		System.out.println("set ladder after");
	}

	// Sets a snake with head in the current cell
	public void setSnake(Snake snake) {
		System.out.println("set snake");
		this.snake = snake;
		System.out.println("set snake after");
	}

	// returns number of the cell
	public int getNumber() {
		return this.number;
	}
}

class Board {
	private int n;
	Cell[] board;
	private Ladder ladder;
	private Snake snake;

	// creates an n-by-n board
	public Board(int n) {
		this.n = n;
		board = new Cell[(int) Math.pow(this.n, 2)];
		for (int i = 0; i < board.length; i++) {
			board[i] = new Cell(i);
		}
	}

	/*
	 * puts a ladder on the map of the game. need to associate ladder with cell at
	 * startPosition
	 */
	public void setCellToLadder(int startPosition, int endPosition) {
		this.ladder = new Ladder(startPosition, endPosition);
		board[startPosition].setLadder(ladder);
		System.out.println("ladder");
	}

	/*
	 * Puts snake on the map of the game. Need to associate the snake with the cell
	 * at headPosition
	 */
	public void setCellToSnake(int headPosition, int tailPosition) {
		this.snake = new Snake(headPosition, tailPosition);
		board[headPosition].setSnake(snake);
		System.out.println("snake");
	}

	// returns all cells of the board
	public Cell[] getCells() {
		return board;
	}
}

class Snake {
	private int headPosition;
	private int tailPosition;

	// creates snake with specified location of head and tail
	public Snake(int headPosition, int tailPosition) {
		this.headPosition = headPosition;
		this.tailPosition = tailPosition;
	}
 
	// returns the position of snake's tail
	public int getTail() {
		return this.tailPosition;
	}

	// returns: head - tail. e.g. 20-11.
	public String toString() {
		return headPosition + " - " + tailPosition + ".";
	}
}

class Ladder {
	private int startPosition;
	private int endPosition;

	/*
	 * creates ladder which connects cells with specified location of start and end
	 * of the ladder
	 */
	public Ladder(int startPosition, int endPosition) {
		this.startPosition = startPosition;
		this.endPosition = endPosition;
	}

	// returns position of the top (end) of the ladder
	public int getTop() {
		return this.endPosition;
	}

	// returns start - end. e.g. 10 - 18.
	public String toString() {
		return this.startPosition + " - " + this.endPosition + ".";
	}
}
