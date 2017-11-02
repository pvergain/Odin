import React from "react";

const LoadingIcon = () => {
  return (
    <div>
      <i className="fa fa-cog fa-spin fa-3x fa-fw" />
      <span className="sr-only">Grading...</span>
    </div>
  );
};

const PassedIcon = () => {
  return (
    <div>
      <i className="fa fa-check-circle fa-3x" />
      <span className="sr-only">Passed</span>
    </div>
  );
};

const ErrorIcon = () => {
  return (
    <div>
      <i className="fa fa-remove fa-3x" />
      <span className="sr-only">Passed</span>
    </div>
  );
};

const IconContainer = props => {
  switch (props.status) {
    case 2: {
      return <PassedIcon />;
    }
    case 3: {
      return <ErrorIcon />;
    }
    default: {
      return <LoadingIcon />;
    }
  }
};

export default IconContainer;
