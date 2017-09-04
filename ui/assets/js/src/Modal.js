import React from 'react';

class Modal extends React.Component {
  render() {
    return (
      <div
        id={`${this.props.modalID}`}
        className="modal fade in"
        aria-hidden="true"
        style={this.props.styles}>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h4 className="modal-title">{this.props.modalTitle}</h4>
            </div>
            <div className="modal-body">{this.props.children}</div>
          </div>
        </div>
      </div>
    );
  }
}

export default Modal;
