# Nasreddin story coverage audit

Audited: 2026-08-10

Source of truth:
`https://nasredin.blogspot.com/2010/12/this-reminds-me-of-story-111-teaching.html`

Local collection:
`src/content/stories/*.md`

## Result

The current repository does **not** contain all 111 stories.

- Source collection: **111 stories**
- Individually represented locally with matching title and/or distinctive story-text evidence: **72**
- Missing locally: **39**
- Arithmetic: **72 + 39 = 111**

The missing stories are source story **#3** and **#74–#111**.

`src/content/stories/8309948.md` does not contain the collection. Its body has
only the subheading “retold by Ioan Tenner” and an image. It contains none of
the 111 story texts.

## Method

1. Fetched the Blogspot page and selected its main `post-body`.
2. Extracted every bold story heading in document order.
3. Excluded the preceding `Foreword`, leaving exactly 111 story headings.
4. Compared those headings with the front-matter titles of all 75 local
   Markdown files.
5. Where titles had changed, checked distinctive text snippets from the story
   body rather than relying on filenames.
6. Treated uncertain thematic/title resemblance as missing rather than as a
   match.

This was a bounded migration audit, not a line-by-line literary comparison.
The 72 positive matches have sufficient title and/or distinctive body-text
evidence to identify the same stories. Many local versions are revised or
expanded and are not verbatim copies of the Blogspot text.

## Reconciliation of the 75 local files

The 75 local Markdown files consist of:

- **72** stories matched to the source collection
- **1** separate foreword: `foreword.md`
- **1** additional story not found among the source 111: `excuses.md`
- **1** nearly empty collection shell: `8309948.md`

Arithmetic: **72 + 1 + 1 + 1 = 75**.

No local file was assigned to more than one source story.

## Present source stories

The repository contains source stories:

- **#1–#2**
- **#4–#73**

The match sequence is continuous across those ranges. Renamed examples checked
with body-text evidence include:

- #7 “One famous strike of scimitar” → `one-famous-strike-of-scimitar.md`,
  locally titled “We do what we can”
- #17 “The other side” → `point-of-view.md`
- #31 “Riding to market” → `the-counsel-you-get.md`
- #34 “The finger…” → `what-i-really-really-want.md`
- #38 “Night walk” → `a-cloak-of-shadow-may-count.md`
- #39 “Rightful price” →
  `for-the-smell-of-food-the-sound-of-money.md`
- #54 “Invocations” → `prayers.md`
- #58 “Make me laugh!” → `the-edge-of-truth.md`
- #60 “They don’t know who I am” → `god-speaks-to-them.md`
- #70 “About learning” →
  `what-use-to-learn-when-you-are-old-70.md`
- #73 “Looking in the mirror” →
  `one-may-need-a-mirror-to-see-the-truth-73.md`

## Missing source stories

1. **#3 — Bull’s eye**
2. **#74 — Just playing**
3. **#75 — Monkey**
4. **#76 — Ask Abdul**
5. **#77 — The key to heaven and hell**
6. **#78 — Nothing**
7. **#79 — A horse saved me**
8. **#80 — God’s kingdom**
9. **#81 — The worth of what you know**
10. **#82 — The once a century scheme**
11. **#83 — Or else!**
12. **#84 — A gift of fruit**
13. **#85 — Too many words**
14. **#86 — The use of boots**
15. **#87 — Conversations with God**
16. **#88 — What it seems and what it is**
17. **#89 — Find the stupid**
18. **#90 — Either or**
19. **#91 — Multiplying with one hundred**
20. **#92 — How much**
21. **#93 — You never know**
22. **#94 — Moving**
23. **#95 — An arm’s length**
24. **#96 — Teaching the perplexed**
25. **#97 — The way**
26. **#98 — Flirting with humility**
27. **#99 — Good food**
28. **#100 — Precise justice**
29. **#101 — Big fish, small fish**
30. **#102 — Last wishes**
31. **#103 — Random acts of kindness**
32. **#104 — Art of begging**
33. **#105 — Just a trifle**
34. **#106 — Bad debt**
35. **#107 — I will fool you**
36. **#108 — Sharing with God**
37. **#109 — Skilful augur**
38. **#110 — The wisdom of the world**
39. **#111 — This shall pass too…**

## Ambiguities checked

### #3 and #64 are different stories

The local file `bulls-eye-this-is-how-i-shoot-64.md` represents source **#64,
“This is how I shoot!”**, not source #3.

Both use archery imagery, and the local title includes “Bulls’ eye”, but their
plots are different:

- #3 is the story of shooting arrows first and painting targets around them.
- #64 is the story of Nasreddin advising the royal archers and then attempting
  to demonstrate his technique.

Therefore #3 remains missing; it must not be counted as a duplicate of #64.

### #10 and #67 are different stories

The similarly named source entries “Seeking and finding” (#10) and “Seek and
you will find” (#67) have distinct story bodies and map to distinct local files:

- #10 → `you-find-things-where-they-are.md`
- #67 → `seek-and-you-will-find-67.md`

### Extra local story

`excuses.md` (“Excuses…”, concerning a neighbour asking to borrow a laundry
rope) has no sufficiently supported counterpart among the source 111. It is an
additional local story, not a substitute for one of the 39 missing entries.

## Index and permalink checks

- Local generated story pages: **75/75 present**
- Deployed story permalinks checked: **75/75 returned HTTP 200**
- Deployed collection index:
  `https://swombat.io/wisdom-tenner/this-reminds-me-of-a-story.html`
  returned HTTP 200 and linked to all 75 local story records.
- The directory-style URL
  `https://swombat.io/wisdom-tenner/this-reminds-me-of-a-story/`
  returned HTTP 404; the configured index permalink is the `.html` URL above.

The index therefore makes all existing local records discoverable, but only 72
of the source collection’s 111 actual stories are currently represented.

## Extracted source title sequence

1. Educating the donkey
2. Filial piety
3. Bull’s eye
4. When the whole world smells fish
5. A time for asking and a time for giving
6. Smuggling common sense
7. One famous strike of scimitar
8. The right perspective
9. Thief in a box
10. Seeking and finding
11. Early bird…
12. Duck soup and kisses through messengers
13. The right place for halwa
14. Sharing is good
15. Seven figs for seven monkeys
16. A handful of sparrows
17. The other side
18. Sitting quietly by the river
19. Word of a donkey
20. Give me your hand!
21. A delightful Turkish bath...
22. Walking on water
23. Stone soup
24. Imam Bayildy
25. Half your life
26. The goat
27. What will I say?
28. Mourning
29. Turn your other cheek
30. Gainful way to loose a wager
31. Riding to market
32. Chastity on the road side
33. Need some money
34. The finger…
35. Language of signs
36. Justice to the people in a garden of truths
37. A silly joke
38. Night walk
39. Rightful price
40. What is air
41. A pot is born
42. Poisonous gift
43. The art of dispute
44. Not much to say
45. The sky is falling
46. Lame duck
47. To talk with kings…
48. Patience please
49. Still going strong
50. Secret of the saints
51. Ibn Khaldoun’s mule
52. Rule of the market
53. Calling names
54. Invocations
55. Son of somebody
56. Virtuous Dreams
57. Funerals
58. Make me laugh!
59. It’s me
60. They don’t know who I am
61. I had the upper hand
62. All we need is answers
63. Stolen
64. This is how I shoot!
65. Hodja’s nail
66. Free lunch
67. Seek and you will find
68. Me again
69. Divine Justice
70. About learning
71. Tamerlane’s elephant
72. The right time
73. Looking in the mirror
74. Just playing
75. Monkey
76. Ask Abdul
77. The key to heaven and hell
78. Nothing
79. A horse saved me
80. God’s kingdom
81. The worth of what you know
82. The once a century scheme
83. Or else!
84. A gift of fruit
85. Too many words
86. The use of boots
87. Conversations with God
88. What it seems and what it is
89. Find the stupid
90. Either or
91. Multiplying with one hundred
92. How much
93. You never know
94. Moving
95. An arm’s length
96. Teaching the perplexed
97. The way
98. Flirting with humility
99. Good food
100. Precise justice
101. Big fish, small fish
102. Last wishes
103. Random acts of kindness
104. Art of begging
105. Just a trifle
106. Bad debt
107. I will fool you
108. Sharing with God
109. Skilful augur
110. The wisdom of the world
111. This shall pass too…

## Recommended next action

Import the 39 missing stories as individual Markdown pages, preserving the
source order as explicit metadata. Replace or remove the misleading empty
`8309948.md` collection shell, and optionally add a redirect from the
directory-style collection URL to `this-reminds-me-of-a-story.html`.
