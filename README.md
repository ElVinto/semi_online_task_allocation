# Semi Online Task Semi Online Task Allocation

This documents describes the different input parameters and output file of the semi-online simulator.

## Command Line

```
`python onlineSolver.py `
or 
`python onlineSolver.py  heuristic error timeStep ordering`
```

- `heu` is label denoting an solving heuristic adapted to the semi-online context. The list of possible heuristic label is presented in the next sections. By default 
heuristic = FMF by default.

- `error` is an integer denoting of uncertainty in the task duration. The possible error in [0, 50, 100, 150, 200, 250].

- `timeStep` is an integer denoting the time period of each time step in seconds, timeStep in `N+`

- `ordering` is a label representing the default task ordering, ordering in [Dec,Inc]


## List of heuristics
- `FMF`
- `my_FF`
- `myBFD`
- `myBFR`
- `myNF`
- `myMRR`
- `myMRD`
- `mySS`
- `myHA`

- `FMF_CPLEX`
- `myFF_CPLEX`
- `myBFD_CPLEX`
- `myBFR_CPLEX`
- `myNF_CPLEX`
- `myMRR_CPLEX`
- `myMRD_CPLEX`
- `mySS_CPLEX`
- `myHA_CPLEX`
### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/ElVinto/semi_online_task_allocation/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
