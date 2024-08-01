package com.mysite.demo.MongoDB.DataSchema;

import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Document(collection = "staticInfo")
@NoArgsConstructor
@AllArgsConstructor
@Data
public class StaticInfo {
    @Id
    private String _id;

    @Field("id")
    private String id;

    @Field("name")
    private String name;

    @Field("addr")
    private String addr;

    @Field("tele")
    private String tele;

    @Field("lon")
    private String lon;

    @Field("lat")
    private String lat;

}
