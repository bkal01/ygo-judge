# ygo-judge

This repo evaluates the performance of LLMs on correctly answering rulings questions in complex trading card games.

## Overview

Yu-Gi-Oh! is a game with over 10,000 unique cards and countless niche, counterintuitive rulings, making it hard for beginners to understand to play the game. Judges, or players who are familiar with the rules enough to pass an official exam and be designated by Konami to answer rulings questions, are few and far between.
If LLMs could answer rulings questions to a high accuracy (at or above the level of humans), players would have a much easier time getting into the game and understanding it.

## Dataset

The [Yu-Gi-Oh! rulings database](https://db.ygoresources.com/recent) contains thousands of questions with official answers from Konami that set the precedent for any future rulings. I sampled 100 rulings from this database to use as an eval set. Here's a sample question and answer:

Q: "If you control a Kycoo the Ghost Destroyer in a Monster Zone, so that its effect that prevents the opponent from banishing cards in the Graveyard is being applied, can the opponent activate Karma Cut?"
A: "Even in the proposed scenario, the opponent can activate Karma Cut. Since the effect of Kycoo the Ghost Destroyer is being applied, cards with the same name in the Graveyard cannot be banished by the effect of Karma Cut and only the monster on the field targeted by Karma Cut is banished. Furthermore, if Kycoo the Ghost Destroyer is targeted for the effect of that Karma Cut, the Kycoo the Ghost Destroyer on the field is banished, and afterwards cards with the same name in the Graveyard are banished."

To answer a question like this, an LLM would need to know the text on both "Karma Cut" and "Kycoo the Ghost Destroyer", the fact that the part of "Karma Cut"'s effect to banish from the graveyard is not a required condition to activate the card, and that "Karma Cut" resolves sequentially, meaning it will first banish a monster, and then try to banish from the GY.

## Approaches

This repo has a few different methods when it comes to using LLMs for answering rulings questions:
1. Base LLMs: using just a regular model (e.g. gpt-4o). This approach yields poor results. LLMs often don't even know the text of the relevant cards and hallucinate effects that don't exist. Although they understand concepts like resolving chains and SEGOC, they fail to apply them to real world scenarios.
2. Base LLMs + card text: providing LLMs with the exact text and stats of the cards mentioned in the query. This greatly improves accuracy and essentially "presents all the facts" of the case to allow an LLM to use whatever reasoning it can to produce an answer.
3. Base LLMs + card text + rulebook: stuffing the context window of the LLM with the entire rulebook of the game, along with the relevant cards. This improves accuracy slightly while using drastically more tokens (an order of magnitude more), which means it's probably not worth it.
4. Base LLMs + card text + RAG: providing LLMs with relevant cards, and then performing RAG over the rules of the game to identify the relevant portions. This yields the highest accuracy and does not spend an absurd amount of tokens per query.

## Running the code

In the base directory, run the command:

```
python main.py --method=<METHOD> --query=<Query>
```

For now, the cards mentioned in the query must exactly match the actual card's name, otherwise it won't be detected and fed as context into the LLM.

## Sample outputs

Q: "I activate Heavy Storm and my opponent has Lord of the Heavenly Prison revealed in their hand and 5 spells/traps set, as well as a face-up field spell. What happens?"

A (Base): When you activate Heavy Storm, Lord of the Heavenly Prison does not prevent the destruction of your opponent's set Spells/Traps, as its effect only protects them from being destroyed if it is on the field. Therefore, your opponent's 5 set Spells/Traps will be destroyed by Heavy Storm, while their field spell remains unaffected. The scenario will resolve with your opponent's 5 set Spells/Traps being destroyed and Lord of the Heavenly Prison remaining in their hand.

A (RAG + Card Texts): When you activate Heavy Storm, it will attempt to destroy all Spells and Traps on the field, but Lord of the Heavenly Prison's effect prevents your opponent's Set cards from being destroyed. Therefore, only the face-up Field Spell will be destroyed while your opponent's 5 Set Spells/Traps remain intact. The resolution of the scenario will result in the destruction of the Field Spell only.

A (actual): [Lord of the Heavenly Prison](https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=16516) states that while it is revealed in the hand, Set cards on the field cannot be destroyed by card effects. So Heavy Storm will destroy the face-up field spell but not the 5 set cards.
