import React from "react";
import AccordionPanel from "./AccordionPanel";

export class Accordion extends React.Component {
  render() {
    return (
      <div className="portlet box green">
        <div className="portlet-title">
          <div className="caption">
            <i className="fa fa-gift" />Course assets
          </div>
          <div className="tools">
            <a
              href="javascript:;"
              className="collapse"
              data-original-title=""
              title=""
            />
          </div>
        </div>
        <div className="portlet-body">
          <div className="panel-group accordion" id="accordion1">
            <AccordionPanel topic={this.props.data[1]} />
          </div>
        </div>
      </div>
    );
  }
}
