import React from "react";

export class Accordion extends React.Component {
  render() {
    return (
      <div className="portlet box green">
        <div className="portlet-title">
          <div className="caption">
            <i className="fa fa-gift" />Accordions
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
            <div className="panel panel-default">
              <div className="panel-heading">
                <h4 className="panel-title">
                  <a
                    className="accordion-toggle"
                    data-toggle="collapse"
                    data-parent="#accordion1"
                    href="#collapse_1"
                    aria-expanded="true"
                  >
                    {" "}Collapsible Group Item #1{" "}
                  </a>
                </h4>
              </div>
              <div
                id="collapse_1"
                className="panel-collapse collapse in"
                aria-expanded="true"
              >
                <div className="panel-body">
                  <p>Sample Accordion</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
