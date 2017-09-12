import React from 'react';

const SolutionTestOutput = props => {
  <div class="well well-sm">
    <h4 class="block">Test results</h4>
    <p>
      {props.testOutput.map(item => {
        item.test_status === 'ok' ? (
          <div class="col-md-1">
            <span className="glyphicon glyphicon-ok-sign" />
          </div>
        ) : (
          <div class="col-md-1">
            <span className="glyphicon glyphicon-remove-sign" />
          </div>
        );
      })}
    </p>
  </div>;
};

export default SolutionTestOutput;
