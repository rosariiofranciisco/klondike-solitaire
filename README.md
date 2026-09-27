# Klondike Solitaire

A Klondike Solitaire game implemented in Python as part of the Workshop on Software Development course.

## About

This project implements the classic Klondike Solitaire card game with a graphical user interface.

The project is developed with an emphasis on:

- Object-oriented design
- Type annotations
- Clean separation between game logic and presentation
- Automated testing
- Algorithmic game-playing bots
- AI/LLM integration

## Game Rules

The game uses a standard 52-card deck without jokers.

### Game Areas

A Klondike game consists of:

- 7 Tableau piles
- 4 Foundation piles
- 1 Stock pile
- 1 Waste pile

### Initial Setup

The 52 cards are shuffled and dealt into the seven Tableau piles.

The Tableau piles contain:
Pile 1 → 1 card
Pile 2 → 2 cards
Pile 3 → 3 cards
Pile 4 → 4 cards
Pile 5 → 5 cards
Pile 6 → 6 cards
Pile 7 → 7 cards

This results in:

- 28 cards in the Tableau
- 24 cards remaining in the Stock

Only the top card of each Tableau pile is initially face-up. All other Tableau cards are face-down.

### Tableau Rules

Cards in the Tableau are built in descending rank with alternating colors.

For example:

K♠
Q♥
J♣
10♦
9♠

is a valid sequence.

Therefore:

- A red card can be placed on a black card of the next higher rank.
- A black card can be placed on a red card of the next higher rank.

For example:

Q♥ → J♣

is valid, while:

Q♥ → J♦

is not valid because both cards are red.

Sequences of face-up cards can be moved together if the entire sequence follows the Tableau rules.

### Revealing Face-Down Cards

When the face-up card on a Tableau pile is moved and a face-down card becomes exposed, that card is turned face-up.

This allows the player to progressively reveal hidden cards.

### Empty Tableau Piles

Only a King can be placed into an empty Tableau pile.

A sequence beginning with a King can also be moved into an empty Tableau pile.

For example:

K♠
Q♥
J♣

can be moved to an empty Tableau pile.

A sequence beginning with a Queen or a lower-ranked card cannot be moved to an empty Tableau pile.

### Foundation Rules

There are four Foundation piles, one for each suit.

Cards are placed into Foundations in ascending order, beginning with the Ace.

For example:

A♠ → 2♠ → 3♠ → 4♠ → ... → Q♠ → K♠

The same rule applies independently to:

- Hearts
- Diamonds
- Clubs
- Spades

Only the next required card of the same suit can be added to a Foundation.

For example, if a Foundation currently contains:

A♥
2♥
3♥

then only the 4♥ can be placed next.

### Stock and Waste

The 24 cards that are not initially dealt to the Tableau form the Stock.

The first version of this project uses the Draw 1 variant.

When the player draws from the Stock:

Stock → Waste

Exactly one card is moved from the Stock to the Waste.

Only the top card of the Waste is available for play.

The top Waste card can be moved to:

- A Tableau pile
- A Foundation

provided that the move is legal.

### Reusing the Stock

When the Stock becomes empty, the Waste can be reused as the Stock.

The cards are transferred back to the Stock while preserving the appropriate order for continued play.

The first version allows unlimited reuse of the Stock.

Other variants, such as limiting the number of Stock reuses, may be considered in future versions.

### Valid Moves

The game supports the following types of moves:

- Stock → Waste
- Waste → Tableau
- Waste → Foundation
- Tableau → Tableau
- Tableau → Foundation
- Foundation → Tableau

### Winning the Game

The game is won when all 52 cards have been placed in the four Foundation piles.

At that point:

4 Foundations × 13 cards = 52 cards

All cards must belong to their corresponding suit Foundation.

## Planned Features

- [ ] Klondike game engine
- [ ] Graphical interface
- [ ] Human vs Human mode
- [ ] Algorithmic bot
- [ ] Multiple bot difficulty levels
- [ ] AI opponent using an LLM API
- [ ] Game statistics
- [ ] Replay system
- [ ] Unit tests
- [ ] Animations and sound
- [ ] Tutorial mode

## Technologies

- Python 3.13
- Pygame
- pytest
- Ruff

## Project Structure

klondike-solitaire/
├── README.md
├── PROMPTS.md
├── pyproject.toml
├── src/
│   └── klondike/
└── tests/