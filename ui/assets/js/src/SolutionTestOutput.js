import React from 'react';

const SolutionTestOutput = props => {
  <div class="well well-sm">
    <h4 class="block">I am a small well</h4>
    <p>
      {props.testOutput.map(item => {
        item.test_status === 'ok' ? (
          <span className="glyphicon glyphicon-ok-sign" />
        ) : (
          <span className="glyphicon glyphicon-remove-sign" />
        );
      })}
    </p>
  </div>;
};

export default SolutionTestOutput;
