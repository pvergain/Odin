import React from "react";

const AccordionPanel = props => {
  console.log(props.topic);
  const collapseID = `collapse_${props.topic.id}`;
  return (
    <div className="panel panel-default">
      <div className="panel-heading">
        <h4 className="panel-title">
          <a
            className="accordion-toggle"
            data-toggle="collapse"
            data-parent="#accordion1"
            href={`#${collapseID}`}
            aria-expanded="true"
          >
            {" "}{props.topic.name}{" "}
          </a>
        </h4>
      </div>
      <div
        id={collapseID}
        className="panel-collapse collapse in"
        aria-expanded="true"
      >
        <div className="panel-body">
          <p>Sample Accordion</p>
        </div>
      </div>
    </div>
  );
};

export default AccordionPanel;
