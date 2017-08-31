import React from "react";
import MaterialsList from "./MaterialsList";

const AccordionPanel = props => {
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
            {props.topic.name}
          </a>
        </h4>
      </div>
      <div
        id={collapseID}
        className="panel-collapse collapse in"
        aria-expanded="true"
      >
        <div className="panel-body">
          <div className="col-md-4">
            <div className="mt-element-ribbon bg-grey-steel">
              <div className="ribbon ribbon-shadow ribbon-clip ribbon-color-success uppercase">
                <div className="ribbon-sub ribbon-clip" />Materials
              </div>
              <div className="ribbon-content">
                <MaterialsList materials={props.topic.materials} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccordionPanel;
