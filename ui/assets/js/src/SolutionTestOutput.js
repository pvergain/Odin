import React from "react";

export const BinarySolutionTestOutput = props => {
  const testCount = props.testOutput.length;
  const passingCount = props.testOutput.filter(item => {
    return item.test_status === "OK";
  }).length;
  let idCount = 0;
  return (
    <div className="col-md-12">
      <div className="well well-sm">
        <div className="container-fluid">
          <center>
            <h3 className="block">Test results</h3>
            <h4 className="block">
              {passingCount} out of {testCount} passed
            </h4>
          </center>
          <div className="col-md-12">
            {props.testOutput.map(item => {
              const identifier = `${props.solutionID}_${idCount++}`;
              return item.test_status === "OK"
                ? <div key={identifier} className="col-md-1">
                    <span
                      className="glyphicon glyphicon-ok fa-2x"
                      style={{ color: "#17c617" }}
                    />
                  </div>
                : <div key={identifier} className="col-md-1">
                    <span
                      className="glyphicon glyphicon-remove fa-2x"
                      style={{ color: "#ff0000" }}
                    />
                  </div>;
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export const SourceCodeSolutionTestOutput = props => {
  return (
    <div className="col-md-12">
      <div className="well well-sm">
        <div className="container-fluid">
          <center>
            <h3 className="block">Test results</h3>
          </center>
          <div className="col-md-12">
            <p>
              {props.testOutput.test_output}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
