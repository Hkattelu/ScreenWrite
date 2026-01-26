# Example Scripts

Complete examples demonstrating the **ScreenWrite** script format.

---

## 🐍 Software Tutorial
*Filename: `tutorial.md`*

```markdown
Title: Python Quick Start
Hook: Write your first line of code today.

## Introduction
Welcome to Python programming. In this tutorial, we will install the language and write our first program together.

## Installing Python
Visit the official Python website and download the latest version. The installer will automatically recommend the correct version for your computer.

[B-roll: screen recording of python.org]
Run the downloaded installer and ensure you check the box that says "Add Python to PATH" before clicking Install.

## Writing Your First Program
Open Visual Studio Code and create a new file named hello.py. Type the print function with the message "Hello World" inside quotation marks.

[B-roll: typing code in VS Code]
Click the green run button in the top right corner. You should see your message appear in the terminal at the bottom.
```

---

## 🎮 Game Walkthrough
*Filename: `walkthrough.md`*

```markdown
Title: Boss Fight Guide
Hook: How to defeat the Final Boss easily.

## Preparation
Before entering the arena, ensure your health is full and your primary weapon is upgraded to level five.

[Image: inventory screen showing level 5 weapon]
Equip the Fire Resistance charm to mitigate the damage from the boss's second phase attacks.

## The First Phase
The boss starts with a heavy slam attack. Dodge to the left and wait for the recovery animation to land three quick hits.

[B-roll: gameplay of player dodging boss slam]
When the boss reaches 50% health, it will retreat to the center of the arena and begin charging its ultimate move.
```

---

## 🛠️ Testing
Test these examples without downloading assets:

```bash
screenwrite tutorial.md --no-fetch --verbose
```