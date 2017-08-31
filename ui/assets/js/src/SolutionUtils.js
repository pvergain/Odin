export const filterSolutions = solution => {
  const studentID = window.props.studentID;
  return (
    solution.student === studentID &&
    (solution.status === 2 || solution.status === 6)
  );
};

export const hasPassingSolutionForTask = task => {
  const solutions = task.solutions;
  console.log(solutions.filter(this.filterSolutions));
  if (solutions.filter(this.filterSolutions).length > 0) {
    return true;
  }
  return false;
};
