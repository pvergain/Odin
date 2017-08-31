import React from "react";

const ListItem = props => {
  const materialUrl = Urls["dashboard:education:material-detail"]({
    material_id: props.material.id
  });

  return (
    <a href={materialUrl} className="list-group-item">
      {props.material.identifier}
    </a>
  );
};

class MaterialsList extends React.Component {
  render() {
    const { materials } = this.props;

    return materials.length > 0
      ? <div className="list-group">
          {materials.map(material => {
            return <ListItem material={material} key={material.id} />;
          })}
        </div>
      : <div />;
  }
}

export default MaterialsList;
