import React from "react";

const ErrorWarning = props => {
  return (
    <div>
      {Object.keys(props.errors).map(key => {
        return (
          <div key={key} className="alert alert-warning">
            {key} : {props.errors[key][0]}
          </div>
        );
      })}
    </div>
  );
};

export default ErrorWarning;
