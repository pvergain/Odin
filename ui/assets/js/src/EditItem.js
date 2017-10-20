import React from 'react';

class EditItem extends React.Component {
  constructor(props) {
    super(props);

    this.handleOnClick = this.handleOnClick.bind(this);
  }

  handleOnClick(e) {
    e.nativeEvent.stopImmediatePropagation();

    window.location.href = this.props.editUrl;
  }

  render() {
    const {size} = this.props;
    const pencil = `fa fa-pencil fa-${size}x`;

    return (
      <a onClick={event => this.handleOnClick(event)}>
        <i className={pencil} />
      </a>
    );
  }
}

export default EditItem;
