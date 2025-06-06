#include <iostream>
#include <cstdlib>
#include <ctime>
#include <string>
using namespace std;

void game() {

    srand(time(0));

    int numberToGuess = rand() % 100 + 1;
    int userGuess;
    int attempts = 0;

    cout << "Welcome to the Number Guessing Game!" << endl;
    cout << "Guess the number between 1 and 100: ";

    do {
        cin >> userGuess; 
        attempts++;

        if (userGuess > numberToGuess) {
            cout << "Too high! Try again: ";
        } else if (userGuess < numberToGuess) {
            cout << "Too low! Try again: ";
        } else {
            cout << "Correct! You guessed the number in " << attempts << " attempts." << endl;
        }

    } while (userGuess != numberToGuess);
}

int main() {
    string playAgain;

    do {
        game();

        cout << "Do you want to play again? (yes/1 to continue): ";
        cin >> playAgain;

    } while (playAgain == "yes" || playAgain == "1");

    cout << "Thanks for playing!" << endl;

    return 0;
}
