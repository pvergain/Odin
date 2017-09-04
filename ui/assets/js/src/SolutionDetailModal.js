import React from 'react';
import Modal from './Modal';

class SolutionDetailModal extends React.Component {
  render() {
    const {modalID, task} = this.props;
    return (
      <Modal modalID={modalID} modalTitle={task} styles={{display: 'block'}}>
        <div className="portlet light">
          <div className="portlet-body">IVAN</div>
        </div>
      </Modal>
    );
  }
}

export default SolutionDetailModal;
