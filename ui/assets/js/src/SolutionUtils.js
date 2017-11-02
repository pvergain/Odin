const MAX_REQUEST_COUNT = 100;

export const filterSolutions = solution => {
  const studentID = window.props.studentID;
  return (
    solution.student === studentID &&
    (solution.status === 2 || solution.status === 6)
  );
};

export const getCountOfPassedTasks = tasks => {
  const passed_tasks = tasks.map(
    task => (hasPassingSolutionForTask(task) ? 1 : 0)
  );
  return passed_tasks.reduce((x, y) => x + y, 0);
};

export const hasPassingSolutionForTask = task => {
  const solutions = task.solutions;
  if (solutions.filter(filterSolutions).length > 0) {
    return true;
  }
  return false;
};

export const pollSolution = (solution_id, setResponseData, pollingURL) => {
  let requestCount = 0;
  const interval = setInterval(() => {
    $.ajax({
      type: "GET",
      url: pollingURL,
      dataType: "json",
      success: data => {
        requestCount++;
        setResponseData(data);
        if (
          data.status === 2 ||
          data.status === 3 ||
          requestCount > MAX_REQUEST_COUNT
        ) {
          clearInterval(interval);
        }
      }
    });
  }, 2000);
};
