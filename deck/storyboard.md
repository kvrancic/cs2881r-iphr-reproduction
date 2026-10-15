# Storyboard

74 slides, one per spoken sentence or phrase of `../talk/transcript.md`. The code is `engine/story/s*.py`; each line below is one `tl.beat`. The cue plate, when a slide has one, sits at the bottom left. In chart scenes a board about 62% of the frame wide stands at the left and the robot (the model under test, at 2x) stands on the ground beside it, reacting and pointing. Each act has its own board: Figure 2 and its split by kind are white paper on legs, the recompute is a terminal on a monitor stand, the rerun and the fact cards stand on a lab bench, geography is a sea chart on a map table. Colour: NO red, YES green, the paper's run blue, our run orange, the fact card aqua, unknown grey, highlights yellow; ticks and crosses are ink.

## Title and the Figure 1 example (1 to 10)
1. Title in smooth type with "ICML paper" (blue) and "our reproduction" (orange) chips; close on the waving robot and the grey scale (camera 1.6x).
2. The robot under the grey scale. Cue "Figure 1".
3. Chat 1 opens: "Ajay River south of Arizaro?"; a "Gemini 2.5 Flash" tag between the scale and the robot.
4. Chat 2 opens with the reverse.
5. A truth tab on top of each window: true NO, true YES. Cue "one true, one false".
6. NO in both windows, an ink tick on the left and an ink cross on the right. Cue "same answer twice".
7. Left: a globe and "hemispheres".
8. Right: two continents and "continents".
9. An ink "reads well" chip on each window's bottom edge; the robot smiles.
10. The scale takes colour and tilts to NO; the robot glances sideways.

## The pairs and Figure 2 (11 to 19)
11. The windows shrink into one pair of a two-row wall of question cards, most of them places; "4,834 pairs". The robot stands at the right under a small scale tilting NO.
12. Books, films, people, places under the wall.
13. One pair, close: ten answer pips per question.
14. Truth tabs; "mostly right" and "mostly wrong" in ink with a tick and a cross.
15. A large flag on the pair and an ink arrow from the scale's NO pan to the wrong answers.
16. Figure 2 on a paper board across the frame: title "Figure 2, share of pairs flagged", axes; the robot stands in front of its empty lower right.
17. The 16 names and bars; "16 models".
18. GPT-4o mini's name on a yellow highlight; 13.49% on its bar, values on the next two.
19. A bulb on each thinking model's name; one bracket over every bar below the dashed 0.5% line, "below 0.5%".

## Four things (20 to 24)
20. Four face-down cards, centred.
21. to 24. Each card flips as it is named: a Figure 2 sheet, two chats, globe with calendar and ruler, an aqua card with a compass.

## The recompute (25 to 31)
25. The Figure 2 sheet of the first card moves into place beside the released data and our code, all large on the ground. Cue "recompute".
26. A terminal: the eight recomputed counts, paper and ours, each with a tick. Cue "exact match".
27. The numbers leave; the ticks move next to the names; "three small discrepancies: 1 the plot, 2 the retest, 3 the ranking" fills the right column.
28. "the plot divides by 4,892" against "pairs in the data 4,834".
29. The retest cutoff on a ruler zoomed to 0.3 to 0.6: used 0.4 (blue outline), stated 0.5 (solid blue).
30. "paper: ranking never changes" above 11 tiny two-model rankings, all parallel.
31. In 8 of the 11 the yellow lines cross: "neighbours swap in 8 of 11".

## The rerun (32 to 42)
32. A tall deck "4,834"; cards fly into a pile: "1,014 pairs, same setup". Cue "a fifth, again".
33. Their judge, grey and switched off with its plug pulled; our labeller with a stamp.
34. "99%, label agreement on their answers" in orange; stamped slips.
35. Four robots with one trait each (GPT-4o mini lively, Llama in a beret, DeepSeek calm, Gemini with a bow), their name tags in one row; a "newer release" ribbon on Gemini's tag.
36. The four name tags become the rows of "size of the lean", paper (blue) against ours (orange).
37. Flagged pairs for GPT-4o mini (146, 139) and Llama (28, 35).
38. to 39. DeepSeek: paper 17 and ours 6; then the striped bar, the paper's answers with our labeller, 12.
40. "DeepSeek V3" over two robots, the paper's run (blue antenna and face) and our run (orange, "?").
41. to 42. "beyond the general lean: same order better again in ours?": an orange bar per model with a white tick for the high end of noise; GPT-4o mini lit first (0.19), then the others (0.05 to 0.07).

## Figure 2 by kind of question (43 to 48)
43. The Figure 2 sheet splits into a globe (geography) and calendar, ruler, cake (dates, sizes, ages). Cue "by kind".
44. On paper: mirrored bars for the 8 checkable models, geography to the left, the rest to the right. Cue "ranking flips by kind".
45. GPT-4o mini on a yellow highlight: 19.6% and 1.4%.
46. QwQ and both Llamas highlighted. Cue "QwQ, Llama: the reverse".
47. Two scales on plinths, the globe in the NO pan of the first, which sinks; its plinth reads 1,269 NO, 122 YES; the second scale grey. Cue "geography: leans NO".
48. The second scale, calendar, ruler and cake in its YES pan, sinks: 590 YES, 8 NO. Cue "dates, sizes, ages: lean YES".

## The two variations (49 to 63)
49. An aqua card, "values in the prompt", and a compass, "geography wording".
50. The aqua card above the question; the robot holds a card; the scale grey. Cue "both true values, above the question".
51. to 52. On the bench: flags outside geography for four models (the fourth "newer model"), then with the card: 57 to 0 in large type.
53. to 54. Llama's flagged pairs, each value asked alone: ten pips, seven lit, "about 7 in 10"; then the guessing line at 5 in 10.
55. Llama (beret, tag above) answers with two written numbers in gold and YES with an ink cross; the big scale tilts YES.
56. A lake question with a large compass; "GPT-4o mini" tag.
57. On the sea chart: GPT-4o mini's flag share by distance between the places: 9%, 9%, 17%, 44%. Cue "far apart: more flags".
58. The farthest bar opens into the lake map (water blue, pins A and B). Cue "far apart: should be easy".
59. "B is southwest of A." in a bubble pointing at the robot. Cue "its answer: southwest".
60. "Southwest, not due west. So: NO."
61. to 63. The wording ladder on the sea chart: the paper's wording in grey, then our runs in orange: reworded 140; "+ further west" (yellow) 31 with its mini map; "+ only due west" 667 of 684 with its mini map.

## The close (64 to 74)
64. The same map twice: "anywhere further west" (yellow), then "due west only" (dashed line).
65. Close on the robot with a zipped mouth, "GPT-4o mini" tag; "two readings?" in a dashed box with an ink cross. Cue "not in any answer we read".
66. Figure 2 again, an orange tick on each of the eight recomputed bars. Cue "the counts reproduce".
67. to 70. The four cards of act 2 return and flip one by one: GPT-4o mini repeats a year later (the same pair in the paper's run and ours); geography, reading of "west"; others, numbers back errors; Llama unsure, still answers.
71. to 73. Three dashed slots, filled one by one: 1,014 pairs not all 4,834; our labeller not their judge; same weights still served?
74. "Thank you", names and the repo link; both chats, the waving robot with the aqua card, the coloured scale and our labeller.
